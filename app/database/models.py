from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import JSON, BigInteger


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str]
    questions_id: Mapped[list[int]] = mapped_column(JSON, default=[])
    answers_id: Mapped[list[int]] = mapped_column(JSON, default=[])

class Question(Base):
    __tablename__ = 'questions'
    
    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    content: Mapped[str]
    author_id: Mapped[int]
    without_answer: Mapped[bool] = mapped_column(default=True)
    answers_id: Mapped[list[int]] = mapped_column(JSON, default=[])

class Answer(Base):
    __tablename__ = 'answers'

    answer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    author_id: Mapped[int]
    question_id: Mapped[int]
    likes: Mapped[int] = mapped_column(default=0)