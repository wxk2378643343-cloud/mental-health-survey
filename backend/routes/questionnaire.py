from flask import Blueprint, request, jsonify
from models import db, Questionnaire, Question, Response, Answer, Result, Alert
from auth_utils import login_required
from scoring import calculate_score
from datetime import datetime

bp = Blueprint('questionnaire', __name__, url_prefix='/api')

# 获取量表列表
@bp.route('/questionnaires', methods=['GET'])
@login_required
def list_questionnaires():
    qs = Questionnaire.query.all()
    return jsonify({'code': 200, 'data': [q.to_dict() for q in qs]})

#量表详情
@bp.route('/questionnaires/<int:qid>', methods=['GET'])
@login_required
def get_questionnaire(qid):
    q = Questionnaire.query.get_or_404(qid)
    return jsonify({'code': 200, 'data': q.to_dict(with_questions=True)})

# 开始一份新问卷
@bp.route('/surveys', methods=['POST'])
@login_required
def start_survey():
    """开始一份新的问卷"""
    data = request.get_json() or {}
    qid = data.get('questionnaire_id')
    if not qid:
        return jsonify({'code': 400, 'msg': '缺少 questionnaire_id'}), 400
    q = Questionnaire.query.get(qid)
    if not q:
        return jsonify({'code': 404, 'msg': '量表不存在'}), 404

    response = Response(user_id=request.current_user.id, questionnaire_id=qid)
    db.session.add(response)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '问卷已创建', 'response_id': response.id,
                    'questionnaire': q.to_dict(with_questions=True)})

# 提交答案并评分
@bp.route('/surveys/<int:rid>/submit', methods=['POST'])
@login_required
def submit_survey(rid):
    """提交答案并计算结果"""
    response = Response.query.get_or_404(rid)
    if response.user_id != request.current_user.id:
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
    if response.status == 'completed':
        return jsonify({'code': 400, 'msg': '该问卷已提交'}), 400

    data = request.get_json() or {}
    answers_data = data.get('answers', {})  # {question_id: value}

    q = Questionnaire.query.get(response.questionnaire_id)
    if len(answers_data) != q.total_items:
        return jsonify({'code': 400, 'msg': f'请完整作答所有{q.total_items}道题目'}), 400

    # 验证每题答案合法性
    answers_map = {}
    for qitem in q.questions:
        key = str(qitem.id)
        if key in answers_data:
            val = answers_data[key]
        elif qitem.id in answers_data:
            val = answers_data[qitem.id]
        else:
            return jsonify({'code': 400, 'msg': f'第{qitem.question_no}题未作答'}), 400
        val = int(val)
        answers_map[qitem.id] = val
        db.session.add(Answer(response_id=rid, question_id=qitem.id, value=val))

    # 计算分数
    score_result = calculate_score(q, answers_map)

    response.status = 'completed'
    response.completed_at = datetime.now()

    result = Result(
        response_id=rid,
        user_id=request.current_user.id,
        questionnaire_id=q.id,
        raw_score=score_result['raw_score'],
        std_score=score_result['std_score'],
        level=score_result['level'],
        level_label=score_result['level_label'],
        interpretation=score_result['interpretation'],
        risk_flag=score_result['risk_flag'],
    )
    db.session.add(result)
    db.session.flush()

    # 高风险自动生成预警
    if score_result['risk_flag']:
        alert = Alert(
            user_id=request.current_user.id,
            result_id=result.id,
            alert_type='high_risk',
            message=f'用户 {request.current_user.username} 在【{q.name}】中得分为'
                    f'{score_result.get("std_score") or score_result["raw_score"]}分，'
                    f'评级为{score_result["level_label"]}，需关注。'
        )
        db.session.add(alert)

    db.session.commit()
    return jsonify({'code': 200, 'msg': '提交成功', 'result': result.to_dict()})


@bp.route('/results', methods=['GET'])
@login_required
def my_results():
    """我的历史结果"""
    results = Result.query.filter_by(user_id=request.current_user.id)\
                          .order_by(Result.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [r.to_dict() for r in results]})

#数据权限
@bp.route('/results/<int:rid>', methods=['GET'])
@login_required
def get_result(rid):
    result = Result.query.get_or_404(rid)
    if result.user_id != request.current_user.id and request.current_user.role != 'admin':
        return jsonify({'code': 403, 'msg': '无权查看'}), 403
    return jsonify({'code': 200, 'data': result.to_dict()})


@bp.route('/stats/me', methods=['GET'])
@login_required
def my_stats():
    """我的统计：各量表最新得分、历史趋势"""
    user_id = request.current_user.id
    results = Result.query.filter_by(user_id=user_id).order_by(Result.created_at).all()

    # 按量表分组
    by_code = {}
    for r in results:
        code = r.questionnaire.code
        if code not in by_code:
            by_code[code] = {'name': r.questionnaire.name, 'history': []}
        by_code[code]['history'].append({
            'date': r.created_at.strftime('%Y-%m-%d'),
            'score': r.std_score if r.std_score else r.raw_score,
            'level_label': r.level_label,
            'level': r.level,
        })

    return jsonify({'code': 200, 'data': by_code})
