from database.database import get_db
from database.models import Post
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from crud.post import post_router
from crud.comments import comment_router


app = FastAPI()

app.include_router(post_router, prefix="/articles", tags=["posts"])
app.include_router(comment_router, prefix="/comments", tags=["comments"])


@app.get("/")
def get_root():
    return HTMLResponse("<h2>API ВКЛЮЧЕНО</h2>")


@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Post.category).distinct().all()
    return [category[0] for category in categories]
