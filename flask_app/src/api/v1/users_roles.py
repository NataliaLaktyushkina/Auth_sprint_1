from database.db_service import get_roles_by_user, assign_role_to_user, detach_role_from_user
from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required
from database.dm_models import Roles, User


@jwt_required()
def users_roles():
    username = request.args.get("username", None)
    if not username:
        return make_response('Username is empty', 401)
    users_roles = get_roles_by_user(username)
    output = [role.name for role in users_roles]
    return jsonify(roles=output)


def assign_role():
    username = request.args.get("username", None)
    role = request.args.get("role", None)
    if not role or not username:
        return make_response('Role or username is empty', 401)
    db_role = Roles.query.filter_by(name=role).first()
    if not db_role:
        return make_response('Role does not exist', 409)
    user_db = User.query.filter_by(login=username).first()
    if not user_db:
        return make_response('User does not exist', 409)
    assign_role_to_user(user_db, db_role)
    return jsonify(msg=f'Role {role} was assigned to user {username}')


def detach_role():
    username = request.args.get("username", None)
    role = request.args.get("role", None)
    if not role or not username:
        return make_response('Role or username is empty', 401)
    db_role = Roles.query.filter_by(name=role).first()
    if not db_role:
        return make_response('Role does not exist', 409)
    user_db = User.query.filter_by(login=username).first()
    if not user_db:
        return make_response('User does not exist', 409)
    detach_role_from_user(user_db, db_role)
    return jsonify(msg=f'Role {role} was  detached from user {username}')
