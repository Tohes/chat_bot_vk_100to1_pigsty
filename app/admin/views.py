from hashlib import sha256

from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema, json_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema, AdminLoginSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from tests.utils import ok_response


class AdminLoginView(View):
    @json_schema(AdminLoginSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        mail = self.data["email"]
        password = self.data['password']
        password = sha256(password.encode()).hexdigest()
        admin = await self.store.admins.get_by_email(mail)
        if admin != None:
            if (admin.password == password) and (admin.email == mail):

                session = await new_session(request=self.request)
                raw_admin = AdminSchema().dump(admin)
                session["admin"] = raw_admin

                return json_response(data= {"id": admin.id, "email": admin.email})
            else:
                raise HTTPForbidden
        else:
            raise HTTPForbidden


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
