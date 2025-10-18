from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .schemas import PostCreate, PostUpdate, PostOut, CategoryEnum, CommentOut
import datetime
from database.database import get_db
from database.models import Post, User, Comment


post_router = APIRouter()


@post_router.get("/{id}", response_model=PostOut)
def get_article(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

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
        comments_count=comments_count
    )


@post_router.get("/", response_model=list[PostOut])
@post_router.get("/category/{category}", response_model=list[PostOut])
def get_articles(category: None | str = None, db: Session = Depends(get_db)):
    query = db.query(Post)
    
    if category:
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


@post_router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
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


@post_router.put("/{id}", response_model=PostOut)
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


@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    db.delete(post)
    db.commit()
    return


@post_router.get("/{id}/comments", response_model=list[CommentOut])
def get_comments(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    comments = db.query(Comment).filter(Comment.post_id == id).order_by(Comment.created_at.desc()).all()
    
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
