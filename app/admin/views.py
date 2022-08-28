from hashlib import sha256

from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from tests.utils import ok_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        print('sloninje_admin')
        data = self.request["data"]
        mail = data['email']
        password = data['password']
        password = sha256(password.encode()).hexdigest()
        admin = await self.store.admins.get_by_email(mail)
        if admin != None:
            if (admin.password == password) and (admin.email == mail):
                session = await new_session(request=self.request)
                raw_admin = AdminSchema().dump(admin)
                session["admin"] = raw_admin

                # def ok_response(data: dict):
                #     return {
                #         "status": "ok",
                #         "data": data,
                #     }
                return json_response(data= {"id": admin.id, "email": admin.email})
                # return json_response(data={"status": "ok", "data": {"id": admin.id, "email": admin.email}})
            else:
                raise HTTPForbidden
        else:
            raise HTTPForbidden

        async def get(self):
            print('megasloninje')

class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
