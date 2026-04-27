from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
# 用户表
class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    email      = db.Column(db.String(100))
    phone      = db.Column(db.String(20))
    age        = db.Column(db.Integer)
    gender     = db.Column(db.String(10))
    role       = db.Column(db.String(10), default='user')
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username,
            'email': self.email, 'phone': self.phone,
            'age': self.age, 'gender': self.gender,
            'role': self.role, 'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 量表定义表
class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    id            = db.Column(db.Integer, primary_key=True)
    code          = db.Column(db.String(20), unique=True, nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text)
    instructions  = db.Column(db.Text)
    total_items   = db.Column(db.Integer, nullable=False)
    scoring_rules = db.Column(db.Text, nullable=False)  # JSON
    use_standard  = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.now)
    questions     = db.relationship('Question', backref='questionnaire', order_by='Question.question_no')

    def to_dict(self, with_questions=False):
        d = {
            'id': self.id, 'code': self.code, 'name': self.name,
            'description': self.description, 'instructions': self.instructions,
            'total_items': self.total_items, 'use_standard': self.use_standard,
        }
        if with_questions:
            d['questions'] = [q.to_dict() for q in self.questions]
        return d

#题目表
class Question(db.Model):
    __tablename__ = 'questions'
    id               = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    question_no      = db.Column(db.Integer, nullable=False)
    content          = db.Column(db.Text, nullable=False)
    opt_0            = db.Column(db.String(100))
    opt_1            = db.Column(db.String(100))
    opt_2            = db.Column(db.String(100))
    opt_3            = db.Column(db.String(100))
    opt_4            = db.Column(db.String(100))
    reverse          = db.Column(db.Boolean, default=False)

    def to_dict(self):
        opts = {}
        for i in range(5):
            v = getattr(self, f'opt_{i}')
            if v:
                opts[i] = v
        return {
            'id': self.id, 'question_no': self.question_no,
            'content': self.content, 'options': opts, 'reverse': self.reverse
        }


class Response(db.Model):
    __tablename__ = 'responses'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    status           = db.Column(db.String(20), default='ongoing')
    started_at       = db.Column(db.DateTime, default=datetime.now)
    completed_at     = db.Column(db.DateTime)
    answers          = db.relationship('Answer', backref='response')


class Answer(db.Model):
    __tablename__ = 'answers'
    id          = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    value       = db.Column(db.Integer, nullable=False)


class Result(db.Model):
    __tablename__ = 'results'
    id               = db.Column(db.Integer, primary_key=True)
    response_id      = db.Column(db.Integer, db.ForeignKey('responses.id'), unique=True, nullable=False)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    raw_score        = db.Column(db.Integer, nullable=False)
    std_score        = db.Column(db.Float)
    level            = db.Column(db.String(20), nullable=False)
    level_label      = db.Column(db.String(20), nullable=False)
    interpretation   = db.Column(db.Text)
    risk_flag        = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.now)
    questionnaire    = db.relationship('Questionnaire')

    def to_dict(self):
        return {
            'id': self.id, 'response_id': self.response_id,
            'questionnaire_id': self.questionnaire_id,
            'questionnaire_name': self.questionnaire.name if self.questionnaire else '',
            'questionnaire_code': self.questionnaire.code if self.questionnaire else '',
            'raw_score': self.raw_score, 'std_score': self.std_score,
            'level': self.level, 'level_label': self.level_label,
            'interpretation': self.interpretation, 'risk_flag': self.risk_flag,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Alert(db.Model):
    __tablename__ = 'alerts'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    result_id  = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    alert_type = db.Column(db.String(30), default='high_risk')
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user       = db.relationship('User')
    result     = db.relationship('Result')

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'username': self.user.username if self.user else '',
            'result_id': self.result_id, 'alert_type': self.alert_type,
            'message': self.message, 'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
