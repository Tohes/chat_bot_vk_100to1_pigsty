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

from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    user_id: int
    body: str


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    user_id: int
    text: str

@dataclass
class Game:
    game_id: int
    user_ids: list[int]
    state: str = 'created'
    answer_id: str = None
    question_id: int = None

@dataclass
class User:
    user_id: int
    state: str
    game_id: int


class Buttons:
    def __init__(self):
        self.start = {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"start_game\"}",
                                "label": "/start"
                            },
                            "color": "negative"
                        }
        self.end = {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"end_game\"}",
                                "label": "/end"
                            },
                            "color": "positive"
                        }
        self.create = {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"create_game\"}",
                                "label": "/create"
                            },
                            "color": "positive"
                        }


        self.answer = {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"answer\"}",
                                "label": "/answer"
                            },
                            "color": "primary"
                        }
        self.join = {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"join_game\"}",
                                "label": "/join"
                            },
                            "color": "secondary"
                        }
        self.exit =     {
                            "action": {
                                "type": "text",
                                "payload": "{\"button\": \"exit\"}",
                                "label": "/exit"
                            },
                            "color": "negative"
                        }
        self.dummy = {
            "action": {
                "type": "text",
                "payload": "{\"button\": \"submit\"}",
                "label": "/don't press!"
            },
            "color": "positive"
        }


