import json
from flask import Blueprint, request, jsonify
from models import db, User, Result, Alert, Questionnaire, Question, Response
from auth_utils import admin_required
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# 用户列表搜索分页
@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page  = request.args.get('page', 1, type=int)
    size  = request.args.get('size', 20, type=int)
    kw    = request.args.get('q', '')
    query = User.query
    if kw:
        query = query.filter(User.username.contains(kw))
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page-1)*size).limit(size).all()
    return jsonify({'code': 200, 'total': total, 'data': [u.to_dict() for u in users]})

#启用禁用
@bp.route('/users/<int:uid>/toggle', methods=['PUT'])
@admin_required
def toggle_user(uid):
    user = User.query.get_or_404(uid)
    if user.role == 'admin':
        return jsonify({'code': 400, 'msg': '不能禁用管理员'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功', 'is_active': user.is_active})

# 测评结果筛选查询
@bp.route('/results', methods=['GET'])
@admin_required
def list_results():
    page    = request.args.get('page', 1, type=int)
    size    = request.args.get('size', 20, type=int)
    risk    = request.args.get('risk', type=int)
    qcode   = request.args.get('code', '')
    query   = Result.query
    if risk is not None:
        query = query.filter(Result.risk_flag == bool(risk))
    if qcode:
        q = Questionnaire.query.filter_by(code=qcode).first()
        if q:
            query = query.filter(Result.questionnaire_id == q.id)
    total = query.count()
    results = query.order_by(Result.created_at.desc()).offset((page-1)*size).limit(size).all()

    data = []
    for r in results:
        d = r.to_dict()
        user = User.query.get(r.user_id)
        d['username'] = user.username if user else ''
        data.append(d)
    return jsonify({'code': 200, 'total': total, 'data': data})

# 预警列表
@bp.route('/alerts', methods=['GET'])
@admin_required
def list_alerts():
    page     = request.args.get('page', 1, type=int)
    size     = request.args.get('size', 20, type=int)
    unread   = request.args.get('unread', type=int)
    query    = Alert.query
    if unread:
        query = query.filter(Alert.is_read == False)
    total  = query.count()
    alerts = query.order_by(Alert.created_at.desc()).offset((page-1)*size).limit(size).all()
    return jsonify({'code': 200, 'total': total, 'data': [a.to_dict() for a in alerts]})


@bp.route('/alerts/<int:aid>/read', methods=['PUT'])
@admin_required
def mark_alert_read(aid):
    alert = Alert.query.get_or_404(aid)
    alert.is_read = True
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已标记为已读'})


@bp.route('/alerts/<int:aid>/unread', methods=['PUT'])
@admin_required
def mark_alert_unread(aid):
    alert = Alert.query.get_or_404(aid)
    alert.is_read = False
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已标记为未读'})


@bp.route('/alerts/read_all', methods=['PUT'])
@admin_required
def mark_all_read():
    Alert.query.update({'is_read': True})
    db.session.commit()
    return jsonify({'code': 200, 'msg': '全部已读'})


@bp.route('/questionnaires', methods=['GET'])
@admin_required
def list_questionnaires():
    page  = request.args.get('page', 1, type=int)
    size  = request.args.get('size', 10, type=int)
    query = Questionnaire.query.order_by(Questionnaire.id)
    total = query.count()
    qs    = query.offset((page - 1) * size).limit(size).all()
    data  = []
    for q in qs:
        d = q.to_dict()
        d['result_count'] = Result.query.filter_by(questionnaire_id=q.id).count()
        data.append(d)
    return jsonify({'code': 200, 'total': total, 'data': data})

#自定义量表
@bp.route('/questionnaires', methods=['POST'])
@admin_required
def create_questionnaire():
    data = request.get_json() or {}

    name         = (data.get('name') or '').strip()
    code         = (data.get('code') or '').strip().upper()
    description  = (data.get('description') or '').strip()
    instructions = (data.get('instructions') or '').strip()
    use_standard = bool(data.get('use_standard', False))
    questions    = data.get('questions', [])   # [{content, options:[str,...], reverse}]
    rules        = data.get('scoring_rules', [])  # [{min,max,level,label}]

    # 基本校验
    if not name:
        return jsonify({'code': 400, 'msg': '问卷名称不能为空'}), 400
    if not code:
        return jsonify({'code': 400, 'msg': '问卷编码不能为空'}), 400
    if not code.replace('_', '').isalnum():
        return jsonify({'code': 400, 'msg': '问卷编码只能含字母、数字、下划线'}), 400
    if Questionnaire.query.filter_by(code=code).first():
        return jsonify({'code': 400, 'msg': f'编码 {code} 已存在，请换一个'}), 400
    if len(questions) < 1:
        return jsonify({'code': 400, 'msg': '至少需要一道题目'}), 400
    if len(rules) < 1:
        return jsonify({'code': 400, 'msg': '至少需要一条评分规则'}), 400

    # 校验题目
    for i, q in enumerate(questions):
        if not (q.get('content') or '').strip():
            return jsonify({'code': 400, 'msg': f'第{i+1}题内容不能为空'}), 400
        opts = [o for o in q.get('options', []) if (o or '').strip()]
        if len(opts) < 2:
            return jsonify({'code': 400, 'msg': f'第{i+1}题至少需要2个选项'}), 400

    # 校验评分规则
    for r in rules:
        if r.get('min') is None or r.get('max') is None:
            return jsonify({'code': 400, 'msg': '评分规则缺少 min/max'}), 400
        if not (r.get('label') or '').strip():
            return jsonify({'code': 400, 'msg': '评分规则缺少等级名称'}), 400
        if not (r.get('level') or '').strip():
            return jsonify({'code': 400, 'msg': '评分规则缺少 level 键'}), 400

    # 写入数据库
    q_obj = Questionnaire(
        code=code, name=name,
        description=description, instructions=instructions,
        total_items=len(questions),
        use_standard=use_standard,
        scoring_rules=json.dumps(rules, ensure_ascii=False),
    )
    db.session.add(q_obj)
    db.session.flush()

    # 写入题目（选项从索引0或1开始，SDS/SAS类型从1开始）
    opt_start = 1 if use_standard else 0
    for idx, qi in enumerate(questions):
        opts = [o.strip() for o in qi.get('options', []) if (o or '').strip()]
        item = Question(
            questionnaire_id=q_obj.id,
            question_no=idx + 1,
            content=qi['content'].strip(),
            reverse=bool(qi.get('reverse', False)),
        )
        for i, opt in enumerate(opts[:5]):
            setattr(item, f'opt_{opt_start + i}', opt)
        db.session.add(item)

    db.session.commit()
    return jsonify({'code': 200, 'msg': '问卷创建成功', 'id': q_obj.id})


@bp.route('/questionnaires/<int:qid>', methods=['DELETE'])
@admin_required
def delete_questionnaire(qid):
    q = Questionnaire.query.get_or_404(qid)
    # 内置量表不允许删除
    BUILTIN = {'PHQ9', 'GAD7', 'SDS', 'SAS'}
    if q.code in BUILTIN:
        return jsonify({'code': 400, 'msg': f'{q.code} 是内置量表，不能删除'}), 400
    # 有测评记录时也不能删除
    if Result.query.filter_by(questionnaire_id=qid).count() > 0:
        return jsonify({'code': 400, 'msg': '该问卷已有测评记录，无法删除'}), 400

    Question.query.filter_by(questionnaire_id=qid).delete()
    db.session.delete(q)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

# 统计面板
@bp.route('/stats', methods=['GET'])
@admin_required
def stats():
    total_users   = User.query.filter_by(role='user').count()
    total_results = Result.query.count()
    risk_count    = Result.query.filter_by(risk_flag=True).count()
    unread_alerts = Alert.query.filter_by(is_read=False).count()

    # 各量表完成次数
    by_questionnaire = db.session.query(
        Questionnaire.name, func.count(Result.id)
    ).join(Result, Questionnaire.id == Result.questionnaire_id)\
     .group_by(Questionnaire.id).all()

    # 各等级分布
    by_level = db.session.query(
        Result.level_label, func.count(Result.id)
    ).group_by(Result.level_label).all()

    # 近7天提交趋势
    from datetime import datetime, timedelta
    trend = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cnt = Result.query.filter(
            func.strftime('%Y-%m-%d', Result.created_at) == d
        ).count()
        trend.append({'date': d, 'count': cnt})

    return jsonify({
        'code': 200,
        'data': {
            'total_users':    total_users,
            'total_results':  total_results,
            'risk_count':     risk_count,
            'unread_alerts':  unread_alerts,
            'by_questionnaire': [{'name': n, 'count': c} for n, c in by_questionnaire],
            'by_level':         [{'label': l, 'count': c} for l, c in by_level],
            'trend':            trend,
        }
    })
