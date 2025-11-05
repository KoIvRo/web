from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CategoryEnum(str, Enum):
    PROGRAMMING = "programming"
    DJANGO = "django"
    PYTHON = "python"
    WEB = "web"
    OTHER = "other"


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    author_name: str
    created_at: str
    comments_count: int

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


class CommentOut(BaseModel):
    id: int
    text: str
    author_name: str
    created_at: str


# Новые схемы
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access: str
    refresh: str

class TokenData(BaseModel):
    user_id: int
    username: str