from database.dm_models import Roles
from flask import jsonify, request, make_response
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from database.db_service import create_role_db, delete_role_db, change_role_db


@jwt_required()
def create_role():
    token = get_jwt()
    users_roles = token['roles']
    if 'manager' not in users_roles:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    role = request.values.get("new_role", None)
    if not role:
        return make_response('New role is empty', 401)

    new_role = create_role_db(role)
    return jsonify(msg=f'Role {role} was successfully created')


@jwt_required()
def delete_role():
    token = get_jwt()
    users_roles = token['roles']
    if 'manager' not in users_roles:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    role = request.json.get("role", None)
    if not role:
        return make_response('Role is empty', 401)

    delete_role_db(role)
    return jsonify(msg=f'Role {role} was successfully deleted')


@jwt_required()
def change_role():
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


@jwt_required()
def roles_list():
    roles = Roles.query.all()
    output = [role.name for role in roles]
    return jsonify(roles=output)
