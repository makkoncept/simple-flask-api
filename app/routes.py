from app import app, db
from flask import jsonify, request, make_response
from app.models import User
from functools import wraps
import jwt
import datetime


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'passwor':
            return f(*args, **kwargs)

        return make_response('Could not verify your login!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the api'})


@app.route('/login', methods=['GET'])
@login_required
def login():
    auth = request.authorization
    token = jwt.encode({'user': auth.get('name'), 'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=20)}, app.config['SECRET_KEY'])
    return jsonify({'message': 'you are logged in', 'token': token.decode('UTF-8')})


@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'you are viewing the protected route'})


@app.route('/createuser', methods=['POST'])
def create():
    user = request.json
    if not user:
        return "shivam not json"
    print(user)
    u = User(name=user.get('name'), info=user.get('info'))
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'user added to database'})


@app.route('/users', methods=['GET'])
# @token_required
def users():
    users = User.query.all()
    users_list = []
    for user in users:
        d = {'name': user.name, 'info': user.info, 'id': user.id}
        users_list.append(d)
    return jsonify({'users': users_list})
