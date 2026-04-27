"""
心理健康问卷系统 API 测试
运行：python -m pytest tests/test_api.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from app import create_app
from models import db, User, Questionnaire


@pytest.fixture(scope='module')
def client():
    # 先覆盖 Config，使用内存数据库
    import config as cfg
    cfg.Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        _seed_in_context()

    with app.test_client() as c:
        yield c


def _seed_in_context():
    """在当前 app_context 内直接写入种子数据，不调用 seed.py 的 create_app"""
    import bcrypt, json
    from seed import QUESTIONNAIRES
    from models import db, User, Questionnaire, Question

    for uname, pw, role in [('admin', 'admin123', 'admin'), ('testuser', 'test123', 'user')]:
        if not User.query.filter_by(username=uname).first():
            h = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            db.session.add(User(username=uname, password=h, role=role, gender='other', age=25))

    for qdata in QUESTIONNAIRES:
        if Questionnaire.query.filter_by(code=qdata['code']).first():
            continue
        q = Questionnaire(
            code=qdata['code'], name=qdata['name'],
            description=qdata['description'], instructions=qdata['instructions'],
            total_items=qdata['total_items'], use_standard=qdata['use_standard'],
            scoring_rules=qdata['scoring_rules'],
        )
        db.session.add(q)
        db.session.flush()
        opt_start = qdata.get('opt_start', 0)
        for qi in qdata['questions']:
            question = Question(questionnaire_id=q.id, question_no=qi['no'],
                                content=qi['content'], reverse=qi['reverse'])
            for i, opt in enumerate(qdata['opts']):
                setattr(question, f'opt_{opt_start + i}', opt)
            db.session.add(question)

    db.session.commit()


@pytest.fixture(scope='module')
def token(client):
    res = client.post('/api/auth/login',
                      json={'username': 'testuser', 'password': 'test123'},
                      content_type='application/json')
    data = res.get_json()
    assert data['code'] == 200
    return data['token']


@pytest.fixture(scope='module')
def admin_token(client):
    res = client.post('/api/auth/login',
                      json={'username': 'admin', 'password': 'admin123'},
                      content_type='application/json')
    data = res.get_json()
    assert data['code'] == 200
    return data['token']


def auth(tk):
    return {'Authorization': f'Bearer {tk}'}


# ────────── Auth ──────────

class TestAuth:
    def test_register_success(self, client):
        res = client.post('/api/auth/register',
                          json={'username': 'newuser99', 'password': 'pass123', 'gender': 'male'},
                          content_type='application/json')
        assert res.get_json()['code'] == 200

    def test_register_duplicate(self, client):
        client.post('/api/auth/register', json={'username': 'dup1', 'password': 'pass123'},
                    content_type='application/json')
        res = client.post('/api/auth/register', json={'username': 'dup1', 'password': 'pass123'},
                          content_type='application/json')
        assert res.get_json()['code'] == 400

    def test_register_short_password(self, client):
        res = client.post('/api/auth/register', json={'username': 'shortpw', 'password': '123'},
                          content_type='application/json')
        assert res.get_json()['code'] == 400

    def test_login_success(self, client):
        res = client.post('/api/auth/login',
                          json={'username': 'testuser', 'password': 'test123'},
                          content_type='application/json')
        data = res.get_json()
        assert data['code'] == 200
        assert 'token' in data

    def test_login_wrong_password(self, client):
        res = client.post('/api/auth/login',
                          json={'username': 'testuser', 'password': 'wrongpw'},
                          content_type='application/json')
        assert res.get_json()['code'] == 401

    def test_me(self, client, token):
        res = client.get('/api/auth/me', headers=auth(token))
        data = res.get_json()
        assert data['code'] == 200
        assert data['user']['username'] == 'testuser'

    def test_me_no_token(self, client):
        res = client.get('/api/auth/me')
        assert res.get_json()['code'] == 401


# ────────── Questionnaire ──────────

class TestQuestionnaire:
    def test_list(self, client, token):
        res = client.get('/api/questionnaires', headers=auth(token))
        data = res.get_json()
        assert data['code'] == 200
        assert len(data['data']) == 4
        codes = [q['code'] for q in data['data']]
        assert 'PHQ9' in codes and 'GAD7' in codes

    def test_get_with_questions(self, client, token):
        res = client.get('/api/questionnaires/1', headers=auth(token))
        data = res.get_json()
        assert data['code'] == 200
        assert 'questions' in data['data']
        assert len(data['data']['questions']) > 0


# ────────── Survey Submit & Score ──────────

class TestSurvey:
    def _get_phq9_id(self, client, token):
        res = client.get('/api/questionnaires', headers=auth(token))
        qs = res.get_json()['data']
        return next(q['id'] for q in qs if q['code'] == 'PHQ9')

    def test_start_and_submit_phq9(self, client, token):
        qid = self._get_phq9_id(client, token)

        # 开始
        res = client.post('/api/surveys', json={'questionnaire_id': qid},
                          headers=auth(token), content_type='application/json')
        data = res.get_json()
        assert data['code'] == 200
        rid = data['response_id']
        questions = data['questionnaire']['questions']

        # 构造答案（全选0分）
        answers = {str(q['id']): 0 for q in questions}

        # 提交
        res2 = client.post(f'/api/surveys/{rid}/submit',
                           json={'answers': answers},
                           headers=auth(token), content_type='application/json')
        data2 = res2.get_json()
        assert data2['code'] == 200
        result = data2['result']
        assert result['raw_score'] == 0
        assert result['level'] == 'none'
        assert result['level_label'] == '无抑郁'
        assert not result['risk_flag']

    def test_submit_high_risk(self, client, token):
        qid = self._get_phq9_id(client, token)
        res = client.post('/api/surveys', json={'questionnaire_id': qid},
                          headers=auth(token), content_type='application/json')
        rid = res.get_json()['response_id']
        questions = res.get_json()['questionnaire']['questions']

        # 全选3分（最高分）
        answers = {str(q['id']): 3 for q in questions}
        res2 = client.post(f'/api/surveys/{rid}/submit',
                           json={'answers': answers},
                           headers=auth(token), content_type='application/json')
        data2 = res2.get_json()
        assert data2['code'] == 200
        result = data2['result']
        assert result['raw_score'] == 27
        assert result['level'] == 'severe'
        assert result['risk_flag'] is True

    def test_submit_incomplete(self, client, token):
        qid = self._get_phq9_id(client, token)
        res = client.post('/api/surveys', json={'questionnaire_id': qid},
                          headers=auth(token), content_type='application/json')
        rid = res.get_json()['response_id']

        # 只提交3题
        res2 = client.post(f'/api/surveys/{rid}/submit',
                           json={'answers': {'1': 0, '2': 1, '3': 2}},
                           headers=auth(token), content_type='application/json')
        assert res2.get_json()['code'] == 400


# ────────── Admin ──────────

class TestAdmin:
    def test_stats(self, client, admin_token):
        res = client.get('/api/admin/stats', headers=auth(admin_token))
        data = res.get_json()
        assert data['code'] == 200
        assert 'total_users' in data['data']

    def test_list_users(self, client, admin_token):
        res = client.get('/api/admin/users', headers=auth(admin_token))
        data = res.get_json()
        assert data['code'] == 200
        assert data['total'] >= 2

    def test_normal_user_no_admin(self, client, token):
        res = client.get('/api/admin/stats', headers=auth(token))
        assert res.get_json()['code'] == 403

    def test_list_alerts(self, client, admin_token):
        res = client.get('/api/admin/alerts', headers=auth(admin_token))
        assert res.get_json()['code'] == 200


# ────────── Scoring Engine（直接测试，无需 DB）──────────

def _make_questionnaire(code, rules_json, use_standard, items):
    """构造轻量 mock 量表对象（不依赖数据库）"""
    class FakeQ:
        pass
    class FakeItem:
        pass
    q = FakeQ()
    q.code = code
    q.use_standard = use_standard
    q.scoring_rules = rules_json
    qs = []
    for i, (reverse,) in enumerate(items):
        qi = FakeItem()
        qi.id = i + 1
        qi.reverse = reverse
        qi.opt_0 = 'a'; qi.opt_1 = 'b'; qi.opt_2 = 'c'; qi.opt_3 = 'd'; qi.opt_4 = None
        qs.append(qi)
    q.questions = qs
    return q

import json as _json

PHQ9_RULES = _json.dumps([
    {'min': 0,  'max': 4,  'level': 'none',              'label': '无抑郁'},
    {'min': 5,  'max': 9,  'level': 'mild',              'label': '轻度抑郁'},
    {'min': 10, 'max': 14, 'level': 'moderate',          'label': '中度抑郁'},
    {'min': 15, 'max': 19, 'level': 'moderately_severe', 'label': '中重度抑郁'},
    {'min': 20, 'max': 27, 'level': 'severe',            'label': '重度抑郁'},
])
SDS_RULES = _json.dumps([
    {'min': 0,  'max': 52, 'level': 'none',     'label': '正常'},
    {'min': 53, 'max': 62, 'level': 'mild',     'label': '轻度抑郁'},
    {'min': 63, 'max': 72, 'level': 'moderate', 'label': '中度抑郁'},
    {'min': 73, 'max': 999,'level': 'severe',   'label': '重度抑郁'},
])


class TestScoring:
    def test_phq9_zero_score(self):
        from scoring import calculate_score
        q = _make_questionnaire('PHQ9', PHQ9_RULES, False, [(False,)] * 9)
        r = calculate_score(q, {i+1: 0 for i in range(9)})
        assert r['raw_score'] == 0
        assert r['level'] == 'none'
        assert not r['risk_flag']

    def test_phq9_moderate(self):
        from scoring import calculate_score
        q = _make_questionnaire('PHQ9', PHQ9_RULES, False, [(False,)] * 9)
        # 9×1 = 9 → mild；调整为 9×1+2 =11 → moderate 用 1,1,1,1,1,1,1,1,3 = 11
        answers = {i+1: 1 for i in range(8)}
        answers[9] = 3  # 总分 11 → moderate
        r = calculate_score(q, answers)
        assert r['level'] == 'moderate'

    def test_phq9_severe(self):
        from scoring import calculate_score
        q = _make_questionnaire('PHQ9', PHQ9_RULES, False, [(False,)] * 9)
        r = calculate_score(q, {i+1: 3 for i in range(9)})
        assert r['raw_score'] == 27
        assert r['level'] == 'severe'
        assert r['risk_flag'] is True

    def test_sds_standard_score(self):
        from scoring import calculate_score
        # 20 题，全正向
        q = _make_questionnaire('SDS', SDS_RULES, True, [(False,)] * 20)
        answers = {i+1: 2 for i in range(20)}   # 原始分 40, 标准分 50
        r = calculate_score(q, answers)
        assert r['std_score'] == round(r['raw_score'] * 1.25)

    def test_reverse_scoring(self):
        from scoring import calculate_score
        # 1 道正向 + 1 道反向，PHQ9 风格 (0-3)
        rules = _json.dumps([{'min': 0, 'max': 6, 'level': 'none', 'label': '正常'}])
        q = _make_questionnaire('PHQ9', rules, False, [(False,), (True,)])
        # 正向选2，反向选2 → 反向变为 3-2=1 → 总分 3
        r = calculate_score(q, {1: 2, 2: 2})
        assert r['raw_score'] == 3
