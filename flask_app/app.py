import datetime
import jwt
from functools import wraps

from flask import Flask
from flask import jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import db
from database.db import init_db
from database.dm_models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisismysecretkey'  # change to  env
INTERVAL = datetime.timedelta(hours=1)


def token_required(func):
    """
    decorator for Movie_API
    :param func:
    :return: function or error message
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        # token = request.args.get('token')  # http://127.0.0.1:5000/route?token=dfalkfdlu8ejlf787
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        # check if token is valid
        try:
            data = jwt.decode(token,  app.config['SECRET_KEY'])
            current_user = User.query.filter_by(login=data['login']).first()

        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return func(current_user, *args, **kwargs)

    return decorated


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(login=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'user': auth.username,
                            'exp': datetime.datetime.utcnow() + INTERVAL},
                           app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['login'] = user.login
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/user/<login>', methods=['GET'])
def get_one_user(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user_data = {}
    user_data['login'] = user.login
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(login=data['login'],
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'})


@app.route('/user/<login>', methods=['PUT'])
def promote_user(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted'})


@app.route('/user/<login>', methods=['DELETE'])
def delete_user(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        return jsonify({'message': 'No user found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User has been deleted'})


def main():
    init_db(app)
    app.app_context().push()
    db.create_all()
    app.run()


if __name__ == '__main__':
    main()
