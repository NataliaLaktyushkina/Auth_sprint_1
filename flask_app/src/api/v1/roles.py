from database.db_service import create_role_db, delete_role_db, change_role_db
from database.dm_models import Roles
from flask import jsonify, request, make_response
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from http import HTTPStatus

@jwt_required()
def create_role():
    token = get_jwt()
    users_roles = token['roles']
    if 'manager' not in users_roles:
        return make_response('Could not verify', HTTPStatus.UNAUTHORIZED,
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})
    role =request.args.get('new_role', None)
    if not role:
        return make_response('New role is empty', HTTPStatus.UNAUTHORIZED)

    new_role = create_role_db(role)
    return jsonify(msg=f'Role {role} was successfully created')


@jwt_required()
def delete_role():
    token = get_jwt()
    users_roles = token['roles']
    if 'manager' not in users_roles:
        return make_response('Could not verify', HTTPStatus.UNAUTHORIZED,
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})

    role = request.args.get("role", None)
    if not role:
        return make_response('Role is empty', HTTPStatus.UNAUTHORIZED)
    db_role = Roles.query.filter_by(name=role).first()
    if not db_role:
        return  make_response('Role does not exist', HTTPStatus.CONFLICT)
    delete_role_db(db_role)
    return jsonify(msg=f'Role {role} was successfully deleted')


@jwt_required()
def change_role():
    token = get_jwt()
    users_roles = token['roles']
    if 'manager' not in users_roles:
        return make_response('Could not verify', HTTPStatus.UNAUTHORIZED, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    role = request.args.get("role", None)
    new_role = request.args.get("new_name", None)
    if not role or not new_role:
        return make_response('Role or new name is empty', HTTPStatus.UNAUTHORIZED)

    change_role_db(role, new_role)
    return jsonify(msg=f'Role {role} was successfully changed')


@jwt_required()
def roles_list():
    roles = Roles.query.all()
    output = [role.name for role in roles]
    return jsonify(roles=output)
