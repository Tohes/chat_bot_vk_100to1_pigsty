from typing import Optional, TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database import db


if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        # DATABASE_URL = "postgresql+asyncpg://postgres:dork@localhost/demo"
        host = self.app.config.database.host
        port = self.app.config.database.port
        password = self.app.config.database.password
        user = self.app.config.database.user
        base = self.app.config.database.database

        DATABASE_URL = f'postgresql+asyncpg://{user}:{password}@{host}/{base}'
        self._db = db
        self._engine = create_async_engine(DATABASE_URL, echo = False, future = True)
        self.session = sessionmaker(bind = self._engine, expire_on_commit= False, class_=AsyncSession)



    async def disconnect(self, *_: list, **__: dict) -> None:
        pass
