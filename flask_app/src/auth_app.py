from datetime import timedelta

from flask import Flask
from flask import request, send_from_directory
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from api.v1.personal_account import sign_up, login, logout, refresh, \
    login_history, change_login, change_password
from api.v1.roles import create_role, delete_role, change_role, roles_list
from api.v1.users_roles import users_roles, assign_role, detach_role
from database.db import db
from database.db import init_db
from database.db_service import get_users_roles
from database.redis_db import redis_app
from utils import settings

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_EXPIRES = timedelta(days=30)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = settings.get_settings().SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


SWAGGER_URL = '/apidocs/'
API_URL = '/static/swagger_config.yml'
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_blueprint)

jwt = JWTManager(app)

app.add_url_rule('/change_login', methods=["POST"], view_func=change_login)
app.add_url_rule('/change_password', methods=["POST"], view_func=change_password)
app.add_url_rule('/login', methods=["POST"], view_func=login)
app.add_url_rule('/login_history', methods=["GET"], view_func=login_history)
app.add_url_rule('/logout', methods=["DELETE"], view_func=logout)
app.add_url_rule('/refresh', methods=["GET"], view_func=refresh)
app.add_url_rule('/sign_up', methods=["POST"], view_func=sign_up)

app.add_url_rule('/create_role', methods=["POST"], view_func=create_role)
app.add_url_rule('/delete_role', methods=["DELETE"], view_func=delete_role)
app.add_url_rule('/change_role', methods=["PUT"], view_func=change_role)
app.add_url_rule('/roles_list', methods=["GET"], view_func=roles_list)

app.add_url_rule('/users_roles', methods=["GET"], view_func=users_roles)
app.add_url_rule('/assign_role', methods=["POST"], view_func=assign_role)
app.add_url_rule('/detach_role', methods=["DELETE"], view_func=detach_role)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    """
    Callback function to check if a JWT exists in the redis blocklist
    """
    user_agent = request.headers['user_agent']
    jti = jwt_payload["jti"]
    key = ':'.join((jti, user_agent))
    token_in_redis = redis_app.get(key)
    return token_in_redis is not None


@jwt.additional_claims_loader
def add_role_to_token(identity):
    """
    callback function used to add additional claims when creating a JWT
    """
    roles = get_users_roles(identity)
    output = [role.name for role in roles]
    return {'roles': output}
############################################


def main():
    init_db(app)
    app.app_context().push()
    db.create_all()
    app.run()


if __name__ == '__main__':
    main()

main()
