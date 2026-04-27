from flask import Blueprint, request, jsonify
from models import db, User
from auth_utils import create_token, login_required
import bcrypt
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 用户注册
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    email    = (data.get('email') or '').strip()
    gender   = data.get('gender', 'other')
    age      = data.get('age')

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400
    if len(username) < 3 or len(username) > 20:
        return jsonify({'code': 400, 'msg': '用户名长度须在3-20字符之间'}), 400
    if len(password) < 6:
        return jsonify({'code': 400, 'msg': '密码不能少于6位'}), 400
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        return jsonify({'code': 400, 'msg': '用户名只能包含字母、数字、下划线或汉字'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, password=pw_hash, email=email or None,
                gender=gender, age=age, role='user')
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id, user.role)
    return jsonify({'code': 200, 'msg': '注册成功', 'token': token, 'user': user.to_dict()})

#用户登录
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401
    if not user.is_active:
        return jsonify({'code': 403, 'msg': '账号已被禁用'}), 403

    token = create_token(user.id, user.role)
    return jsonify({'code': 200, 'msg': '登录成功', 'token': token, 'user': user.to_dict()})


@bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'code': 200, 'user': request.current_user.to_dict()})


@bp.route('/update_profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or {}
    user = request.current_user
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'age' in data:
        user.age = data['age']
    if 'gender' in data:
        user.gender = data['gender']
    if data.get('new_password'):
        if len(data['new_password']) < 6:
            return jsonify({'code': 400, 'msg': '新密码不能少于6位'}), 400
        user.password = bcrypt.hashpw(data['new_password'].encode(), bcrypt.gensalt()).decode()
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'user': user.to_dict()})
