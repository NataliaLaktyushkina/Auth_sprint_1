from datetime import timedelta

from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jti, get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash
from flasgger import Swagger, SwaggerView, Schema, fields

from database.db_service import add_record_to_login_history, \
    create_user, change_login, change_password
from database.dm_models import User, LoginHistory
from database.redis_db import redis_app

from models.pers_acc_models import JWT_Tokens

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_EXPIRES = timedelta(days=30)

storage = redis_app


class Sing_UpView(SwaggerView):
    parameters = [
        {
            "name": "username",
            'in': "query",
            "type": "string",
            "required": True
        },
        {
            "name": "password",
            'in': "query",
            "type": "string",
            "required": True
        }
    ]
    responses = {
        200: {
            "description": "User's sing up. Get access and refresh JWT-tokens",
            "schema": JWT_Tokens
        },
        401: {
            "description": "Login and password required"
        }
    }

    def post(self):
        username = request.values.get("username", None)
        password = request.values.get("password", None)
        if not username or not password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        new_user = create_user(username, password)

        access_token = create_access_token(identity=new_user.id, fresh=True)
        refresh_token = create_refresh_token(identity=new_user.id)
        user_agent = request.headers['user_agent']

        # запись в БД попытки входа
        add_record_to_login_history(new_user, user_agent)

        # запись в Redis refresh token
        key = ':'.join(('user_refresh', user_agent, get_jti(refresh_token)))
        storage.set(key, str(new_user.id), ex=REFRESH_EXPIRES)

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)


class LoginView(SwaggerView):
    parameters = []
    security = {"BasicAuth": []}
    responses = {
        200: {
            "description": "Login into account. Get access and refresh JWT-tokens",
            "schema": JWT_Tokens
        },
        401: {
            "description": "Could not verify login or password"
        }
    }
    # components = {
    #     "securitySchemes": {
    #         "BasicAuth": {
    #             "type": "http",
    #             "scheme": "basic"}}}
    #

    def post(self):

        auth = request.authorization

        if not auth.username or not auth.password:
            # username = request.values.get("username", None)
            # password = request.values.get("password", None)
            # if not username or not password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        user = User.query.filter_by(login=auth.username).first()
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        if check_password_hash(user.password, auth.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            user_agent = request.headers['user_agent']

            # запись в БД попытки входа
            add_record_to_login_history(user, user_agent)

            # запись в Redis refresh token
            key = ':'.join(('user_refresh', user_agent, get_jti(refresh_token)))
            storage.set(key, str(user.id), ex=REFRESH_EXPIRES)

            return jsonify(access_token=access_token,
                           refresh_token=refresh_token)

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


# user’s refresh token must also be revoked when logging out;
# otherwise, this refresh token could just be used to generate a new access token.
class LogoutView(SwaggerView):
    # security = {"bearerAuth": []}
    responses = {
        200: {
            "description": "revoke access/refresh token",
        },
        401: {
            "description": "Could not verify token"
        }
    }

    @jwt_required(verify_type=False)
    def delete(self):
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        user_agent = request.headers['user_agent']
        key = ':'.join((jti, user_agent))
        redis_app.set(key, "", ex=ACCESS_EXPIRES)

        # Returns "Access token revoked" or "Refresh token revoked"
        return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@jwt_required(refresh=True)
def refresh():
    """
    выдаёт новую пару токенов (access и refresh) в обмен на корректный refresh-токен.
    """
    identity = get_jwt_identity()  # user_id
    # Проверка, что пользователь тот же
    token = get_jwt()
    jti = token["jti"]
    user_agent = request.headers['user_agent']
    key = ':'.join(('user_refresh', user_agent, jti))
    user_db = storage.get(key).decode('utf-8')
    if identity == user_db:
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        # запись в Redis refresh token
        key = ':'.join(('user_refresh', user_agent, get_jti(refresh_token)))
        storage.set(key, identity, ex=REFRESH_EXPIRES)

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@jwt_required()
def login_history():
    """
    получение пользователем своей истории входов в аккаунт
    """
    user_id = get_jwt_identity()

    history = LoginHistory.query.filter_by(user_id=user_id). \
        order_by(LoginHistory.auth_date.desc()). \
        limit(10)
    output = []
    for record in history:
        record_data = {'user_agent': record.user_agent,
                       'auth_date': record.auth_date}
        output.append(record_data)
    return jsonify(login_history=output)



class ChangeLogin(SwaggerView):
    parameters = [
        {
            "name": "new_username",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "Username was successfully changed"
        },
        400: {
            "description": "Login already existed"
        }
    }

    @jwt_required()
    def post(self):

        new_username = request.json.get('new_username')
        user = User.query.filter_by(login=new_username).first()
        if user:
            return make_response('Login already existed', 400)

        identity = get_jwt_identity()  # user_id - current_user
        current_user = User.query.filter_by(id=identity).first()
        change_login(current_user, new_username)

        return jsonify(msg='Login successfully changed')



class ChangePassword(SwaggerView):
    parameters = [
        {
            "name": "new_password",
            'in': "query",
            "type": "string",
            "required": True
        },
    ]
    responses = {
        200: {
            "description": "Password was successfully changed"
        },
        400: {
            "description": "Could not change password"
        }
    }

    @jwt_required()
    def post(self):

        new_password = request.json.get('new_password')

        identity = get_jwt_identity()  # user_id - current_user
        current_user = User.query.filter_by(id=identity).first()
        change_password(current_user, new_password)

        access_token = create_access_token(identity=identity, fresh=True)
        refresh_token = create_refresh_token(identity=identity)
        user_agent = request.headers['user_agent']

        # запись в Redis refresh token
        key = ':'.join(('user_refresh', user_agent, get_jti(refresh_token)))
        storage.set(key, str(identity), ex=REFRESH_EXPIRES)

        return jsonify(msg='Password successfully changed',
                       access_token=access_token,
                       refresh_token=refresh_token)

