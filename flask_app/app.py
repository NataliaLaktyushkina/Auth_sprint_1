from datetime import timedelta

from flask import Flask
from flask import request
from flask_jwt_extended import JWTManager
from flask_restx import Api

from api.v1.personal_account import SingUpView, LoginView, LogoutView, refresh, \
    login_history, ChangeLogin, ChangePassword
from api.v1.roles import CreateRoleView, DeleteRoleView,  ChangeRoleView, RolesListView
from api.v1.users_roles import UsersRolesListView, AssignRoleToUserView, DetachRoleView
from database.db import db
from database.db import init_db
from database.db_service import get_users_roles
from database.redis_db import redis_app
from utils import settings
from flasgger import Swagger

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_EXPIRES = timedelta(days=30)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = settings.get_settings().SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES
app.config['SWAGGER'] = {'title': 'Auth API'}

swagger_template = {"components": {
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
           },
        "BasicAuth": {
            "type": "http",
            "scheme": "basic",
           }}}
}

swagger = Swagger(app, template=swagger_template)
# authorizations = {
#     'Bearer Auth': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'Authorization'
#     },
# }
# authorizations = {
#     'Basic Auth': {
#         'type': 'basic',
#         'in': 'header',
#         'name': 'Authorization'
#     },
# }
jwt = JWTManager(app)

app.add_url_rule('/change_login', methods=["POST"], view_func=ChangeLogin.as_view('change_login'))
app.add_url_rule('/change_password', methods=["POST"], view_func=ChangePassword.as_view('change_password'))
app.add_url_rule('/login', methods=["POST"], view_func=LoginView.as_view('login'))
app.add_url_rule('/login_history', methods=["GET"], view_func=login_history)
app.add_url_rule('/logout', methods=["DELETE"], view_func=LogoutView.as_view('logout'))
app.add_url_rule('/refresh', methods=["GET"], view_func=refresh)
app.add_url_rule('/sign_up', methods=["POST"], view_func=SingUpView.as_view('sign_up'))

app.add_url_rule('/create_role', methods=["POST"], view_func=CreateRoleView.as_view('create_role'))
app.add_url_rule('/delete_role', methods=["DELETE"], view_func=DeleteRoleView.as_view('delete_role'))
app.add_url_rule('/change_role', methods=["PUT"], view_func=ChangeRoleView.as_view('change_role'))
app.add_url_rule('/roles_list', methods=["GET"], view_func=RolesListView.as_view('roles_list'))

app.add_url_rule('/users_roles', methods=["GET"], view_func=UsersRolesListView.as_view('users_roles'))
app.add_url_rule('/assign_role', methods=["POST"], view_func=AssignRoleToUserView.as_view('assign_role'))
app.add_url_rule('/detach_role', methods=["DELETE"], view_func=DetachRoleView.as_view('detach_role'))


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
