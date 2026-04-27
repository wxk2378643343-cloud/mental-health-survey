import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from models import db

# Flask应用工厂模式，初始化所有组件
def create_app():
    # 创建flask实例
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    CORS(app, resources={r'/api/*': {'origins': '*'}}, supports_credentials=True)
    db.init_app(app)

    from routes.auth import bp as auth_bp
    from routes.questionnaire import bp as q_bp
    from routes.admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(q_bp)
    app.register_blueprint(admin_bp)

    # 服务 Vue 打包产物（dist 目录）
    dist_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api'):
            return jsonify({'code': 404, 'msg': 'Not found'}), 404
        full = os.path.join(dist_dir, path)
        if path and os.path.exists(full):
            return send_from_directory(dist_dir, path)
        return send_from_directory(dist_dir, 'index.html')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print('心理健康问卷系统启动: http://127.0.0.1:5000')
    print('请先运行 python seed.py 初始化数据')
    app.run(debug=True, host='0.0.0.0', port=5000)
