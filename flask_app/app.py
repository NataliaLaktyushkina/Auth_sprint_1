from datetime import timedelta

from flask import Flask
from flask import request
from flask_jwt_extended import JWTManager
from flask_restx import Api

from api.v1.personal_account import Sing_UpView, LoginView, LogoutView, refresh, \
    login_history, change_login, change_password
from database.db import db
from database.db import init_db
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

# swagger = Swagger(app, template=swagger_template)
# swagger = Swagger(app)
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
swagger = Swagger(app, template=swagger_template)


app.add_url_rule('/change_login', methods=["POST"], view_func=change_login)
app.add_url_rule('/change_password', methods=["POST"], view_func=change_password)
app.add_url_rule('/login', methods=["POST"], view_func=LoginView.as_view('login'))
app.add_url_rule('/login_history', methods=["GET"], view_func=login_history)
app.add_url_rule('/logout', methods=["DELETE"], view_func=LogoutView.as_view('logout'))
app.add_url_rule('/refresh', methods=["GET"], view_func=refresh)
app.add_url_rule('/sign_up', methods=["POST"], view_func=Sing_UpView.as_view('sign_up'))


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


############################################

def main():
    init_db(app)
    app.app_context().push()
    db.create_all()
    app.run()


if __name__ == '__main__':
    main()
