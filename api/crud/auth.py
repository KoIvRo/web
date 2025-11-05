from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from crud.schemas import UserCreate, UserLogin, Token

# ИМПОРТИРУЕМ ФУНКЦИИ ИЗ auth.py
from auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    verify_refresh_token,
    get_password_hash,
    get_user_by_username,
    get_current_user  # ДОБАВЛЯЕМ ИМПОРТ
)

router = APIRouter(prefix="/api", tags=["authentication"])

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate, 
    response: Response, 
    db: Session = Depends(get_db)
):
    # Проверяем, что пользователь не существует
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Проверяем совпадение паролей
    if user_data.password1 != user_data.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Проверяем длину пароля
    if len(user_data.password1) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters long"
        )
    
    # Проверяем длину username
    if len(user_data.username) < 3 or len(user_data.username) > 150:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be between 3 and 150 characters"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password1)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Создаем токены
    access_token = create_access_token(new_user.id, new_user.username)
    refresh_token = create_refresh_token(new_user.id, new_user.username)
    
    # Устанавливаем куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=15*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    return {
        "access": access_token,
        "refresh": refresh_token
    }

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, 
    response: Response, 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Создаем токены
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)
    
    # Устанавливаем куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=15*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True, 
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    return {
        "access": access_token,
        "refresh": refresh_token
    }

@router.post("/token/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response, 
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("user_id")
    username = payload.get("username")
    
    # Проверяем что пользователь существует
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Создаем новые токены
    new_access_token = create_access_token(user_id, username)
    new_refresh_token = create_refresh_token(user_id, username)
    
    # Обновляем куки
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=15*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    return {
        "access": new_access_token,
        "refresh": new_refresh_token
    }

@router.post("/logout")
async def logout(response: Response):
    # Удаляем куки
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"message": "Successfully logged out"}

# ТЕПЕРЬ ЭТОТ ЭНДПОИНТ БУДЕТ РАБОТАТЬ
@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)  # ТЕПЕРЬ ФУНКЦИЯ ДОСТУПНА
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }