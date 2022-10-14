# from app.store.database.sqlalchemy_base import db
#
# from sqlalchemy import (
#     CHAR,
#     CheckConstraint,
#     Column,
#     ForeignKey,
#     ForeignKeyConstraint,
#     Index,
#     Integer,
#     NUMERIC,
#     PrimaryKeyConstraint,
#     TIMESTAMP,
#     Text,
#     VARCHAR,
#     String,
#     Boolean
# )
# from sqlalchemy.orm import relationship
#
# # список активных пользователей
# class ActiveModel(db):
#     __tablename__ = "active"
#     user_id = Column(Integer, primary_key = True)
#     state = Column(String)
#     game_id = Column(Integer, nullable = True)
#
# # список пользователей в игре
# # нужна для того, чтобы хранить список пользователей в игре
# class UserModel(db):
#     __tablename__ = "users"
#     user_id = Column(Integer, primary_key = True)
#     game_id = Column(Integer, ForeignKey('games.game_id', ondelete="CASCADE"))
#     __table_args__ = {'extend_existing': True}
#
# # список id_ответов, которые еще не отгадали
# # при создании игры загружаем в нее все id ответов из базы
# # и по мере отгадывания удаляем оттуда
# class AnsModel(db):
#     __tablename__ = "id_answers"
#     id = Column(Integer, primary_key = True)
#     question_id = Column(Integer, ForeignKey('questions.id', ondelete="CASCADE"), nullable = False)
#     __table_args__ = {'extend_existing': True}
#
# # список id вопросов, на которые еще не отгадали все ответы
# # если отгаданы все ответы для вопроса, то вопрос удаляется
# class QModel(db):
#     __tablename__ = "id_questions"
#     q_id = Column(Integer, primary_key = True)
#     game = Column(Integer, ForeignKey('games.game_id', ondelete="CASCADE"), nullable = False)
#     answers = relationship(AnsModel)
#     __table_args__ = {'extend_existing': True}
#
# # список активных игр
# class GameModel(db):
#     __tablename__ = "games"
#     game_id = Column(Integer, primary_key = True, autoincrement = True)
#     users = relationship(UserModel)
#     state = Column(String)
#     questions = relationship(QModel)
#     __table_args__ = {'extend_existing': True}