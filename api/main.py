from database.database import get_db
from database.models import Post
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from crud.post import post_router
from crud.comments import comment_router
from crud.auth import router as auth_router  # ИМПОРТИРУЕМ НОВЫЙ РОУТЕР
from auth import JWTAuthMiddleware

app = FastAPI()

# CORS для React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(JWTAuthMiddleware)

# Подключаем роутеры
app.include_router(post_router, prefix="/articles", tags=["posts"])
app.include_router(comment_router, prefix="/comments", tags=["comments"])
app.include_router(auth_router, tags=["authentication"])  # ДОБАВЛЯЕМ АУТЕНТИФИКАЦИЮ

@app.get("/")
def get_root():
    return HTMLResponse("<h2>API ВКЛЮЧЕНО</h2>")

@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Post.category).distinct().all()
    return [category[0] for category in categories]