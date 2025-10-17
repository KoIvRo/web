from database import *
from sqlalchemy.orm import Session
# import os
# import django
# from django.shortcuts import get_object_or_404

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
# django.setup()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import datetime
# from main.models import Post


class CategoryEnum(str, Enum):
    PROGRAMMING = "programming"
    DJANGO = "django"
    PYTHON = "python"
    WEB = "web"
    OTHER = "other"


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    author_name: str
    created_at: str
    comments_count: int

class CommentOut(BaseModel):
    id: int
    text: str
    author_name: str
    created_at: str


class PostCreate(BaseModel):
    title: str = Field(None, min_length=1, max_length=200)
    content: str = Field(None, min_length=1)
    category: str
    author_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str]


class CommentCreate(BaseModel):
    text: str = Field(None, min_length=1)
    author_id: int
    post_id: int


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)


@app.get("/")
def get_root():
    return HTMLResponse("<h2>API ВКЛЮЧЕНО</h2>")

@app.get("/articles/{id}", response_model=PostOut)
def get_article(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    # post = get_object_or_404(Post, id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    author = db.query(User).filter(User.id == post.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")

    comments_count = db.query(Comment).filter(Comment.post_id == id).count()
    
    return PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        category=post.category,
        author_id=post.author_id,
        author_name=author.username,
        created_at=post.created_at.isoformat() if post.created_at else "",
        # comments_count=post.comments.count()
        comments_count=comments_count
    )

@app.get("/articles/", response_model=list[PostOut])
@app.get("/articles/category/{category}", response_model=list[PostOut])
def get_articles(category: None | str = None, db: Session = Depends(get_db)):
    query = db.query(Post)
    # posts = Post.objects.all().select_related("author").prefetch_related("comments").order_by('-created_at')
    
    if category:
        # posts = posts.filter(category=category)
        query = query.filter(Post.category == category)
    
    posts = query.order_by(Post.created_at.desc()).all()
    
    result_list = []
    for post in posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        
        result_list.append(PostOut(
            id=post.id,
            title=post.title,
            content=post.content,
            category=post.category,
            author_id=post.author_id,
            author_name=author.username if author else "Unknown",
            created_at=post.created_at.isoformat() if post.created_at else "",
            comments_count=comments_count
        ))
    
    return result_list


@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Post.category).distinct().all()
    return [category[0] for category in categories]


@app.post("/articles/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_articles(post_data: PostCreate, db: Session = Depends(get_db)):
    author = db.query(User).filter(User.id==post_data.author_id).first()

    if not author:
        raise HTTPException(status_code=404)

    if not post_data.category in [category.value for category in CategoryEnum]:
        raise HTTPException(status_code=404)

    new_post = Post(
        title = post_data.title,
        content = post_data.content,
        category = post_data.category,
        author_id = post_data.author_id,
        created_at = datetime.datetime.now()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return PostOut(
        id = new_post.id,
        title = new_post.title,
        content = new_post.content,
        category = new_post.category,
        author_id = new_post.author_id,
        author_name = author.username,
        created_at = new_post.created_at.isoformat() if new_post.created_at else "",
        comments_count = 0
    )

@app.delete("/articles/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    db.delete(post)
    db.commit()
    return


@app.put("/articles/{id}", response_model=PostOut)
def update_article(id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.category is not None:
        post.category = data.category

    db.commit()
    db.refresh(post)

    author = db.query(User).filter(User.id == post.author_id).first()
    comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()

    return PostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        category=post.category,
        author_id=post.author_id,
        author_name=author.username if author else "Unknown",
        created_at=post.created_at.isoformat() if post.created_at else "",
        comments_count=comments_count
    )

@app.get("/comments/")
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments

@app.get("/comments/{id}")
def get_comment(id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.id==id).first()


@app.get("/articles/{id}/comments", response_model=list[CommentOut])
def get_comments(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    # post = get_object_or_404(Post, id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    comments = db.query(Comment).filter(Comment.post_id == id).order_by(Comment.created_at.desc()).all()
    # comments = post.comments.all().select_related('author').order_by('-created_at')
    
    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.author_id).first()
        
        result.append(CommentOut(
            id=comment.id,
            text=comment.text,
            author_name=author.username if author else "Unknown",
            created_at=comment.created_at.isoformat() if comment.created_at else ""
        ))
    
    return result


@app.post("/articles/{id}/comments")
def create_comments(id: int, comment_data: CommentCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        text=comment_data.text,
        author_id=comment_data.author_id,
        post_id=id,
        created_at=datetime.datetime.now()
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return

@app.delete("/comments/{id}")
def comment_delete(id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id==id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return

@app.put("/comments/{id}")
def comment_update(id: int, data: CommentUpdate, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id==id).first()

    if data.text is not None:
        comment.text = data.text

    db.commit()
    db.refresh(comment)

    return