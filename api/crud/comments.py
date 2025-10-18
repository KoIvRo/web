from fastapi import APIRouter, Depends, HTTPException
from database.models import Comment, Post
from database.database import get_db
from sqlalchemy.orm import Session
from .schemas import CommentCreate, CommentUpdate
import datetime


comment_router = APIRouter()


@comment_router.get("/")
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments


@comment_router.get("/{id}")
def get_comment(id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.id==id).first()


@comment_router.delete("/{id}")
def comment_delete(id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id==id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return


@comment_router.put("/{id}")
def comment_update(id: int, data: CommentUpdate, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id==id).first()

    if data.text is not None:
        comment.text = data.text

    db.commit()
    db.refresh(comment)

    return


@comment_router.post("/")
def create_comments(comment_data: CommentCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        text=comment_data.text,
        author_id=comment_data.author_id,
        post_id=comment_data.post_id,
        created_at=datetime.datetime.now()
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return