from dataclasses import dataclass
from app.store.database.sqlalchemy_base import db

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    NUMERIC,
    PrimaryKeyConstraint,
    TIMESTAMP,
    Text,
    VARCHAR,
    String,
    Boolean
)
from sqlalchemy.orm import relationship


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Question:
    id: int | None
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String, nullable=False, unique = True)
    __table_args__ = {'extend_existing': True}


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(Integer, primary_key = True)
    title = Column(String, nullable = False)
    is_correct = Column(Boolean, nullable = False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable = False)
    __table_args__ = {'extend_existing': True}

class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String, nullable=False, unique=True)
    theme_id = Column(Integer, ForeignKey('themes.id', ondelete='CASCADE'), nullable = False)
    answers = relationship(AnswerModel)
    __table_args__ = {'extend_existing': True}

# class AnswerModel(db):
#     __tablename__ = "answers"
#     id = Column(Integer, primary_key = True)
#     title = Column(String, nullable = False)
#     is_correct = Column(Boolean, nullable = False)
#     question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable = False)
#     __table_args__ = {'extend_existing': True}

