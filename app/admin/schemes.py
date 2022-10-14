from marshmallow import Schema, fields


class AdminLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class AdminSchema(Schema):
    id = fields.Int()
    email = fields.Str()
