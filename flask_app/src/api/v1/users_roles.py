from flasgger import SwaggerView
from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required

from database.db_service import get_roles_by_user, assign_role_to_user, detach_role_from_user


@jwt_required()
def users_roles(self):
    username = request.json.get("username", None)
    if not username:
        return make_response('Username is empty', 401)
    users_roles = get_roles_by_user(username)
    output = [role.name for role in users_roles]
    return jsonify(roles=output)


def assign_role(self):
    username = request.json.get("username", None)
    role = request.json.get("role", None)
    if not role or not username:
        return make_response('Role or username is empty', 401)

    assign_role_to_user(username, role)
    return jsonify(msg=f'Role {role} was assigned to user {username}')


def detach_role(self):
    username = request.json.get("username", None)
    role = request.json.get("role", None)
    if not role or not username:
        return make_response('Role or username is empty', 401)

    detach_role_from_user(username, role)
    return jsonify(msg=f'Role {role} was  detached from user {username}')
