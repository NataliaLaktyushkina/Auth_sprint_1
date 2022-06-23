from flasgger import SwaggerView
from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required

from database.db_service import get_roles_by_user, assign_role_to_user, detach_role_from_user


class UsersRolesListView(SwaggerView):
    tags = ["Managing User's roles"]
    parameters = [
        {
            "name": "username",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]

    @jwt_required()
    def get(self):
        username = request.json.get("username", None)
        if not username:
            return make_response('Username is empty', 401)
        users_roles = get_roles_by_user(username)
        output = [role.name for role in users_roles]
        return jsonify(roles=output)


class AssignRoleToUserView(SwaggerView):
    tags = ["Managing User's roles"]
    parameters = [
        {
            "name": "username",
            'in': "query",
            "type": "string",
            "required": True
        },
        {
            "name": "role",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "Role was assigned to user"
        },
        401: {
            "description": "Role or username is empty"
        },
        500: {
            "description": "Could not assign role to user"
        }
    }

    def post(self):
        username = request.json.get("username", None)
        role = request.json.get("role", None)
        if not role or not username:
            return make_response('Role or username is empty', 401)

        assign_role_to_user(username, role)
        return jsonify(msg=f'Role {role} was assigned to user {username}')


class DetachRoleView(SwaggerView):
    tags = ["Managing User's roles"]
    parameters = [
        {
            "name": "username",
            'in': "query",
            "type": "string",
            "required": True
        },
        {
            "name": "role",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "Role was assigned to user"
        },
        401: {
            "description": "Role or username is empty"
        },
        500: {
            "description": "Could not assign role to user"
        }
    }

    def delete(self):
        username = request.json.get("username", None)
        role = request.json.get("role", None)
        if not role or not username:
            return make_response('Role or username is empty', 401)

        detach_role_from_user(username, role)
        return jsonify(msg=f'Role {role} was  detached from user {username}')
