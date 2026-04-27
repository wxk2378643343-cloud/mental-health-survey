"""
初始数据：四套标准量表 + 默认管理员账号
运行方式：python seed.py
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User, Questionnaire, Question
import bcrypt

QUESTIONNAIRES = [
    {
        'code': 'PHQ9',
        'name': 'PHQ-9 抑郁症筛查量表',
        'description': 'Patient Health Questionnaire-9，用于筛查和评估抑郁症严重程度，广泛应用于临床和研究领域。',
        'instructions': '在过去两周内，您被以下问题困扰的频率是多少？请根据实际情况选择最符合的选项。',
        'total_items': 9,
        'use_standard': False,
        'scoring_rules': json.dumps([
            {'min': 0,  'max': 4,  'level': 'none',              'label': '无抑郁'},
            {'min': 5,  'max': 9,  'level': 'mild',              'label': '轻度抑郁'},
            {'min': 10, 'max': 14, 'level': 'moderate',          'label': '中度抑郁'},
            {'min': 15, 'max': 19, 'level': 'moderately_severe', 'label': '中重度抑郁'},
            {'min': 20, 'max': 27, 'level': 'severe',            'label': '重度抑郁'},
        ], ensure_ascii=False),
        'questions': [
            {'no': 1,  'content': '做事时提不起劲或没有兴趣', 'reverse': False},
            {'no': 2,  'content': '感到心情低落、沮丧或绝望', 'reverse': False},
            {'no': 3,  'content': '入睡困难、睡不安稳或睡眠过多', 'reverse': False},
            {'no': 4,  'content': '感觉疲倦或没有活力', 'reverse': False},
            {'no': 5,  'content': '食欲不振或吃太多', 'reverse': False},
            {'no': 6,  'content': '觉得自己很糟糕，或觉得自己很失败，或让自己或家人失望', 'reverse': False},
            {'no': 7,  'content': '对事物专注有困难，例如看报纸或看电视时', 'reverse': False},
            {'no': 8,  'content': '动作或说话速度缓慢到别人已经察觉，或正好相反，烦躁或坐立不安、动来动去的情况比平时更多', 'reverse': False},
            {'no': 9,  'content': '有不如死掉或用某种方式伤害自己的念头', 'reverse': False},
        ],
        'opts': ['完全不会', '几天', '一半以上的天数', '几乎每天'],  # 0-3
    },
    {
        'code': 'GAD7',
        'name': 'GAD-7 广泛性焦虑量表',
        'description': 'Generalized Anxiety Disorder-7，用于筛查广泛性焦虑障碍，是临床常用的焦虑评估工具。',
        'instructions': '在过去两周内，您被以下问题困扰的频率是多少？',
        'total_items': 7,
        'use_standard': False,
        'scoring_rules': json.dumps([
            {'min': 0,  'max': 4,  'level': 'none',     'label': '无焦虑'},
            {'min': 5,  'max': 9,  'level': 'mild',     'label': '轻度焦虑'},
            {'min': 10, 'max': 14, 'level': 'moderate', 'label': '中度焦虑'},
            {'min': 15, 'max': 21, 'level': 'severe',   'label': '重度焦虑'},
        ], ensure_ascii=False),
        'questions': [
            {'no': 1, 'content': '感觉紧张、焦虑或烦躁', 'reverse': False},
            {'no': 2, 'content': '不能停止或无法控制担忧', 'reverse': False},
            {'no': 3, 'content': '对各种各样的事情担忧过多', 'reverse': False},
            {'no': 4, 'content': '很难放松下来', 'reverse': False},
            {'no': 5, 'content': '由于不安而无法静坐', 'reverse': False},
            {'no': 6, 'content': '变得容易烦恼或急躁', 'reverse': False},
            {'no': 7, 'content': '感到似乎将有可怕的事情发生而害怕', 'reverse': False},
        ],
        'opts': ['完全不会', '几天', '一半以上的天数', '几乎每天'],
    },
    {
        'code': 'SDS',
        'name': 'SDS 抑郁自评量表',
        'description': 'Self-rating Depression Scale，Zung编制，含20道题，通过标准分评估抑郁程度。',
        'instructions': '请根据您最近一周的实际感受，选择最符合您情况的答案。1=没有或很少时间；2=少部分时间；3=相当多时间；4=绝大部分或全部时间。',
        'total_items': 20,
        'use_standard': True,
        'scoring_rules': json.dumps([
            {'min': 0,  'max': 52, 'level': 'none',     'label': '正常'},
            {'min': 53, 'max': 62, 'level': 'mild',     'label': '轻度抑郁'},
            {'min': 63, 'max': 72, 'level': 'moderate', 'label': '中度抑郁'},
            {'min': 73, 'max': 999,'level': 'severe',   'label': '重度抑郁'},
        ], ensure_ascii=False),
        'questions': [
            {'no': 1,  'content': '我感到情绪沮丧、郁闷',             'reverse': False},
            {'no': 2,  'content': '我感到早晨心情最好',               'reverse': True},
            {'no': 3,  'content': '我要哭泣或想哭',                   'reverse': False},
            {'no': 4,  'content': '我夜间睡眠不好',                   'reverse': False},
            {'no': 5,  'content': '我吃饭像平时一样多',               'reverse': True},
            {'no': 6,  'content': '我与异性接触时和以往一样感到愉快', 'reverse': True},
            {'no': 7,  'content': '我感到体重减轻',                   'reverse': False},
            {'no': 8,  'content': '我为便秘感到烦恼',                 'reverse': False},
            {'no': 9,  'content': '我的心跳比平时快',                 'reverse': False},
            {'no': 10, 'content': '我无故感到疲劳',                   'reverse': False},
            {'no': 11, 'content': '我的头脑像往常一样清楚',           'reverse': True},
            {'no': 12, 'content': '我做事情像平时一样不感到困难',     'reverse': True},
            {'no': 13, 'content': '我感到坐卧不安，难以保持平静',     'reverse': False},
            {'no': 14, 'content': '我对未来感到有希望',               'reverse': True},
            {'no': 15, 'content': '我比平时更容易激怒',               'reverse': False},
            {'no': 16, 'content': '我觉得做出决定是容易的',           'reverse': True},
            {'no': 17, 'content': '我感到自己是有用的和不可缺少的人', 'reverse': True},
            {'no': 18, 'content': '我的生活很有意义',                 'reverse': True},
            {'no': 19, 'content': '假若我死了别人会生活得更好',       'reverse': False},
            {'no': 20, 'content': '我仍旧喜爱自己平时喜爱的东西',     'reverse': True},
        ],
        'opts': ['没有或很少时间', '少部分时间', '相当多时间', '绝大部分或全部时间'],  # 1-4
        'opt_start': 1,
    },
    {
        'code': 'SAS',
        'name': 'SAS 焦虑自评量表',
        'description': 'Self-rating Anxiety Scale，Zung编制，含20道题，通过标准分评估焦虑程度。',
        'instructions': '请根据您最近一周的实际感受，选择最符合您情况的答案。1=没有或很少时间；2=少部分时间；3=相当多时间；4=绝大部分或全部时间。',
        'total_items': 20,
        'use_standard': True,
        'scoring_rules': json.dumps([
            {'min': 0,  'max': 49, 'level': 'none',     'label': '正常'},
            {'min': 50, 'max': 59, 'level': 'mild',     'label': '轻度焦虑'},
            {'min': 60, 'max': 69, 'level': 'moderate', 'label': '中度焦虑'},
            {'min': 70, 'max': 999,'level': 'severe',   'label': '重度焦虑'},
        ], ensure_ascii=False),
        'questions': [
            {'no': 1,  'content': '我感到比往常更加神经过敏和焦虑',   'reverse': False},
            {'no': 2,  'content': '我无缘无故感到害怕',               'reverse': False},
            {'no': 3,  'content': '我容易心烦意乱或感到恐慌',         'reverse': False},
            {'no': 4,  'content': '我感到我的身体好像被分成几块',     'reverse': False},
            {'no': 5,  'content': '我感到事事都很顺利，不会有倒霉的事情发生', 'reverse': True},
            {'no': 6,  'content': '我的手臂和腿抖动',                 'reverse': False},
            {'no': 7,  'content': '我因头痛、颈痛和背痛而苦恼',       'reverse': False},
            {'no': 8,  'content': '我感到无力且容易疲劳',             'reverse': False},
            {'no': 9,  'content': '我感到很平静，能安静坐下来',       'reverse': True},
            {'no': 10, 'content': '我感到我的心跳较快',               'reverse': False},
            {'no': 11, 'content': '我因阵阵的眩晕而不舒服',           'reverse': False},
            {'no': 12, 'content': '我有过昏厥的感觉或觉得要昏厥',     'reverse': False},
            {'no': 13, 'content': '我能够毫不困难地呼气和吸气',       'reverse': True},
            {'no': 14, 'content': '我的手指和脚趾感到麻木和刺痛',     'reverse': False},
            {'no': 15, 'content': '我因胃痛和消化不良而苦恼',         'reverse': False},
            {'no': 16, 'content': '我必须时常排尿',                   'reverse': False},
            {'no': 17, 'content': '我的手总是温暖而干燥',             'reverse': True},
            {'no': 18, 'content': '我觉得脸发红发烫',                 'reverse': False},
            {'no': 19, 'content': '我容易入睡，晚上休息很好',         'reverse': True},
            {'no': 20, 'content': '我做噩梦',                         'reverse': False},
        ],
        'opts': ['没有或很少时间', '少部分时间', '相当多时间', '绝大部分或全部时间'],
        'opt_start': 1,
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # 管理员账号
        if not User.query.filter_by(username='admin').first():
            pw = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            admin = User(username='admin', password=pw, email='admin@mhsurvey.com',
                         role='admin', gender='other', age=30)
            db.session.add(admin)
            print('Created admin user (admin / admin123)')

        # 测试用户
        if not User.query.filter_by(username='testuser').first():
            pw = bcrypt.hashpw('test123'.encode(), bcrypt.gensalt()).decode()
            user = User(username='testuser', password=pw, email='test@example.com',
                        role='user', gender='female', age=22)
            db.session.add(user)
            print('Created test user (testuser / test123)')

        # 量表数据
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
            opts = qdata['opts']
            for qi in qdata['questions']:
                question = Question(
                    questionnaire_id=q.id,
                    question_no=qi['no'],
                    content=qi['content'],
                    reverse=qi['reverse'],
                )
                for i, opt in enumerate(opts):
                    setattr(question, f'opt_{opt_start + i}', opt)
                db.session.add(question)

            print(f'Created questionnaire: {qdata["code"]}')

        db.session.commit()
        print('Seed completed.')


if __name__ == '__main__':
    seed()
