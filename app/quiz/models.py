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
    id: int
    title: str

@dataclass
class Question:
    id: int
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
    score = Column(Integer, nullable = False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable = False)
    __table_args__ = {'extend_existing': True}

class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String, nullable=False, unique=True)
    theme_id = Column(Integer, ForeignKey('themes.id', ondelete='CASCADE'), nullable = False)
    answers = relationship(AnswerModel)
    __table_args__ = {'extend_existing': True}

# список активных пользователей
class ActiveModel(db):
    __tablename__ = "active"
    user_id = Column(Integer, primary_key = True)
    state = Column(String)
    game_id = Column(Integer, nullable = True)
    __table_args__ = {'extend_existing': True}

# список пользователей в игре
# нужна для того, чтобы хранить список пользователей в игре
class UserModel(db):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True)
    game_id = Column(Integer, ForeignKey('games.game_id', ondelete="CASCADE"))
    __table_args__ = {'extend_existing': True}

# список id_ответов, которые еще не отгадали
# при создании игры загружаем в нее все id ответов из базы
# и по мере отгадывания удаляем оттуда
class AnsModel(db):
    __tablename__ = "id_answers"
    id = Column(Integer, primary_key = True)
    question_id = Column(Integer, ForeignKey('id_questions.q_id', ondelete="CASCADE"), nullable = False)
    __table_args__ = {'extend_existing': True}

# список id вопросов, на которые еще не отгадали все ответы
# если отгаданы все ответы для вопроса, то вопрос удаляется
class QModel(db):
    __tablename__ = "id_questions"
    q_id = Column(Integer, primary_key = True)
    game = Column(Integer, ForeignKey('games.game_id', ondelete="CASCADE"), nullable = False)
    answers = relationship(AnsModel)
    __table_args__ = {'extend_existing': True}

# список активных игр
class GameModel(db):
    __tablename__ = "games"
    game_id = Column(Integer, primary_key = True)
    users = relationship(UserModel)
    state = Column(String)
    questions = relationship(QModel)
    answer_id = Column(String, nullable = True)
    question_id = Column(Integer, nullable = True)
    __table_args__ = {'extend_existing': True}

class ScoreModel(db):
    __tablename__ = "scores"
    id = Column(Integer, primary_key = True, autoincrement = True)
    game_id = Column(Integer, ForeignKey('games.game_id', ondelete="CASCADE"), nullable = False)
    user_id = Column(Integer)
    score = Column(Integer)
    __table_args__ = {'extend_existing': True}
