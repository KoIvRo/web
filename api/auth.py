from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from database.database import get_db
from database.models import User
from sqlalchemy.orm import Session

SECRET_KEY = "KEY"
ALGORITHM = "HS256"
REFRESH_SECRET_KEY = "REFRESH_KEY"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Существующие функции
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None

# НОВЫЕ ФУНКЦИИ ДЛЯ АУТЕНТИФИКАЦИИ
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(user_id: int, username: str):
    expires_delta = timedelta(minutes=15)
    expire = datetime.now() + expires_delta
    
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "access",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int, username: str):
    expires_delta = timedelta(days=7)
    expire = datetime.now() + expires_delta
    
    payload = {
        "user_id": user_id,
        "username": username,
        "type": "refresh", 
        "exp": expire
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    
    # Проверяем пароль
    if not verify_password(password, user.password):
        return False
    return user

# ЗАВИСИМОСТЬ ДЛЯ ПОЛУЧЕНИЯ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    access_token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]

    if not access_token:
        access_token = request.cookies.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing token")

    payload = verify_jwt(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пропускаем аутентификацию для публичных эндпоинтов
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/api/register", "/api/login", "/api/token/refresh", "/"]:
            return await call_next(request)
            
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

        if not access_token:
            access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Missing token")

        payload = verify_jwt(access_token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        request.state.user = payload
        return await call_next(request)