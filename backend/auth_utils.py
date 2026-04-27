"""JWT 工具 + 登录装饰器"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models import User

# 生成token
def create_token(user_id: int, role: str) -> str:
    from datetime import datetime, timedelta
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRE_HOURS'])
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

#验证token
def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request() -> str | None:
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return request.cookies.get('token')


def login_required(f):
    # 登录验证装饰器
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'code': 401, 'msg': '未登录'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'Token 无效或已过期'}), 401
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'code': 401, 'msg': '用户不存在或已禁用'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

#管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'code': 401, 'msg': '未登录'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'Token 无效或已过期'}), 401
        if payload.get('role') != 'admin':
            return jsonify({'code': 403, 'msg': '无管理员权限'}), 403
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'code': 401, 'msg': '用户不存在'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated
