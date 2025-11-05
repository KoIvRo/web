from database.database import get_db
from database.models import Post
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from crud.post import post_router
from crud.comments import comment_router
from crud.auth import router as auth_router
from auth import JWTAuthMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы включая OPTIONS
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.add_middleware(JWTAuthMiddleware)


app.include_router(post_router, prefix="/articles", tags=["posts"])
app.include_router(comment_router, prefix="/comments", tags=["comments"])
app.include_router(auth_router, tags=["authentication"])

@app.get("/")
def get_root():
    return HTMLResponse("<h2>API ВКЛЮЧЕНО</h2>")

@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Post.category).distinct().all()
    return [category[0] for category in categories]