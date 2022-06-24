from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView, Schema, fields


class JWT_Tokens(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
