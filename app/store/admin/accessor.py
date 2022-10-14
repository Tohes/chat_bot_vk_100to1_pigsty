import typing
from hashlib import sha256

from aiohttp.web_exceptions import HTTPForbidden
from sqlalchemy import select, text, insert
from sqlalchemy.engine import ChunkedIteratorResult

from app.store import Database

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application

class AdminAccessor(BaseAccessor):

    async def connect(self, app: "Application"):
        # TODO: создать админа по данным в config.yml здесь
        self.app = app
        email = self.app.config.admin.email
        password = self.app.config.admin.password
        await self.create_admin(email,password)

    async def get_by_email(self, email: str) -> Admin | None:
        mail = email
        Q1 = select(AdminModel).where(AdminModel.email == 'admin@admin.com')
        # query = text("SELECT email, password, id FROM admins WHERE email = 'admin@admin.com'")
        dbs = Database(self.app)
        await dbs.connect()
        # password = sha256('admin'.encode()).hexdigest()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q1)

        result2 = result.scalars().all()
        if result2:
            ans = Admin(result2[0].id, result2[0].email, result2[0].password)
        else:
            ans = None


        return ans

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(email=email, password=sha256(password.encode()).hexdigest(), id=1)
        query = text("SELECT email, password, id FROM admins")
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(query)
        results_as_dict = result.mappings().all()
        print(results_as_dict)
        if not results_as_dict:
            pwd = sha256(password.encode()).hexdigest()
            # U1 = insert(AdminModel).values(id = 1, email = 'admin@admin.com', password = pwd)
            U1 = insert(AdminModel).values(id=1, email= self.app.config.admin.email \
                                           , password=self.app.config.admin.password)
            # dbs = Database(self.app)
            # await dbs.connect()
            async with dbs.session() as session:
                await session.execute(U1)
                await session.commit()
        else:
            print('admin already exists!')
        return admin
