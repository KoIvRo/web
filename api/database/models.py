from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "auth_user"
    
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(128))
    last_login = Column(DateTime, nullable=True)  # необязательное
    is_superuser = Column(Boolean, default=False)
    username = Column(String(150), unique=True, index=True)
    last_name = Column(String(150), default="")
    email = Column(String(254), unique=True, index=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime, default=datetime.now)
    first_name = Column(String(150), default="")

class Post(Base):
    __tablename__ = "main_post"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    category = Column(String(20))
    content = Column(Text)
    author_id = Column(Integer)
    created_at = Column(DateTime)


class Comment(Base):
    __tablename__ = "main_comment"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    text = Column(Text)
    post_id = Column(Integer)
    author_id = Column(Integer)