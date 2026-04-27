"""
量表评分引擎
支持：PHQ-9、GAD-7、SDS、SAS
"""
import json
import math


def calculate_score(questionnaire, answers_map: dict) -> dict:
    """
    questionnaire: Questionnaire ORM对象
    answers_map: {question_id: value}
    返回: {raw_score, std_score, level, level_label, interpretation, risk_flag}
    """
    questions = questionnaire.questions
    raw_score = 0

    for q in questions:
        val = answers_map.get(q.id)
        if val is None:
            continue
        if q.reverse:
            # PHQ9/GAD7: 0-3 → 3-0; SDS/SAS: 1-4 → 4-1 (即 5-val)
            if questionnaire.use_standard:
                val = 5 - val
            else:
                max_val = max(k for k in [q.opt_0, q.opt_1, q.opt_2, q.opt_3] if k is not None)
                # PHQ9/GAD7 最大值是3
                val = 3 - val
        raw_score += val

    # 标准分换算（SDS/SAS）
    std_score = None
    if questionnaire.use_standard:
        std_score = round(raw_score * 1.25)

    # 分级
    rules = json.loads(questionnaire.scoring_rules)
    score_for_level = std_score if std_score is not None else raw_score
    level = 'none'
    level_label = '正常'
    for rule in rules:
        lo = rule.get('min', 0)
        hi = rule.get('max', 9999)
        if lo <= score_for_level <= hi:
            level = rule['level']
            level_label = rule['label']
            break

    # 风险预警：重度或中重度
    risk_flag = level in ('severe', 'moderately_severe')

    # 文字解读
    interpretation = _get_interpretation(questionnaire.code, level, score_for_level)

    return {
        'raw_score': raw_score,
        'std_score': std_score,
        'level': level,
        'level_label': level_label,
        'interpretation': interpretation,
        'risk_flag': risk_flag
    }


def _get_interpretation(code: str, level: str, score: int) -> str:
    intps = {
        'PHQ9': {
            'none':              f'得分{score}分，无抑郁症状。您的情绪状态良好，请继续保持健康的生活方式。',
            'mild':              f'得分{score}分，存在轻度抑郁症状。建议关注自身情绪变化，适当参与社交活动和有氧运动，必要时寻求心理咨询。',
            'moderate':          f'得分{score}分，存在中度抑郁症状。建议尽快寻求专业心理咨询，制定干预计划。',
            'moderately_severe': f'得分{score}分，存在中重度抑郁症状。强烈建议尽快就医，接受专业评估和治疗。',
            'severe':            f'得分{score}分，存在重度抑郁症状。请立即寻求专业医疗帮助，如有自伤想法请拨打心理援助热线 400-161-9995。',
        },
        'GAD7': {
            'none':     f'得分{score}分，无焦虑症状。您的心理状态良好。',
            'mild':     f'得分{score}分，存在轻度焦虑症状。建议学习放松技巧，如深呼吸、冥想，关注睡眠质量。',
            'moderate': f'得分{score}分，存在中度焦虑症状。建议寻求心理咨询，接受认知行为疗法干预。',
            'severe':   f'得分{score}分，存在重度焦虑症状。请尽快就医，接受专业评估与治疗。',
        },
        'SDS': {
            'none':     f'标准分{score}分，无抑郁。您的心理状态正常。',
            'mild':     f'标准分{score}分，轻度抑郁。建议关注情绪健康，适当倾诉和运动。',
            'moderate': f'标准分{score}分，中度抑郁。建议寻求专业心理援助。',
            'severe':   f'标准分{score}分，重度抑郁。请立即寻求医疗帮助。',
        },
        'SAS': {
            'none':     f'标准分{score}分，无焦虑。心理状态良好。',
            'mild':     f'标准分{score}分，轻度焦虑。建议学习压力管理技巧。',
            'moderate': f'标准分{score}分，中度焦虑。建议寻求心理咨询。',
            'severe':   f'标准分{score}分，重度焦虑。请尽快就医评估。',
        },
    }
    return intps.get(code, {}).get(level, '评分完成，请咨询专业人员解读结果。')
