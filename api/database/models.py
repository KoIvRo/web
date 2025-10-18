from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    username = Column(String(150))
    email = Column(String(254))


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