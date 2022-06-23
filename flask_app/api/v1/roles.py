from flasgger import SwaggerView
from flask import jsonify, request, make_response
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required

from database.db_service import create_role_db, delete_role_db, change_role_db
from database.dm_models import Roles


class CreateRoleView(SwaggerView):
    tags = ["Managing Roles"]
    parameters = [
        {
            "name": "new_role",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "New role was created"
        },
        401: {
            "description": "New role is empty"
        },
        500: {
            "description": "Role already existed in database"
        }
    }

    @jwt_required()
    def post(self):
        token = get_jwt()
        users_roles = token['roles']
        if 'manager' not in users_roles:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
        role = request.json.get("new_role", None)
        if not role:
            return make_response('New role is empty', 401)

        new_role = create_role_db(role)
        return jsonify(msg=f'Role {role} was successfully created')


class DeleteRoleView(SwaggerView):
    tags = ["Managing Roles"]
    parameters = [
        {
            "name": "role",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "New role was deleted"
        },
        409: {
            "description": "Role doesnt exist in database"
        }
    }

    @jwt_required()
    def delete(self):
        token = get_jwt()
        users_roles = token['roles']
        if 'manager' not in users_roles:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        role = request.json.get("role", None)
        if not role:
            return make_response('Role is empty', 401)

        delete_role_db(role)
        return jsonify(msg=f'Role {role} was successfully deleted')


class ChangeRoleView(SwaggerView):
    tags = ["Managing Roles"]
    parameters = [
        {
            "name": "role",
            'in': "query",
            "type": "string",
            "required": True
        },
        {
            "name": "new_name",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "Role was renamed"
        },
        409: {
            "description": "Role doesnt exist in database"
        }
    }

    @jwt_required()
    def put(self):
        token = get_jwt()
        users_roles = token['roles']
        if 'manager' not in users_roles:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        role = request.json.get("role", None)
        new_role = request.json.get("new_name", None)
        if not role or not new_role:
            return make_response('Role or new name is empty', 401)

        change_role_db(role, new_role)
        return jsonify(msg=f'Role {role} was successfully changed')


class RolesListView(SwaggerView):
    tags = ["Managing Roles"]

    @jwt_required()
    def get(self):
        roles = Roles.query.all()
        output = [role.name for role in roles]
        return jsonify(roles=output)
