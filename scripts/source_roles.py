from pathlib import Path

CANONICAL_SOURCE_ROLES = {
    'teacher_ppt',
    'textbook',
    'official_handout',
    'syllabus',
    'user_note',
    'source_question',
    'historical_exam',
    'assignment_or_quiz',
    'senior_note',
    'existing_vault',
    'external_supplement',
    'model_inference_pending_verification',
    'unclassified_source',
}

LEGACY_SOURCE_ROLE_MAP = {
    'teacher/textbook': 'teacher_ppt',
    'user_notes': 'user_note',
    'historical_questions': 'historical_exam',
    'senior_notes': 'senior_note',
    'other': 'unclassified_source',
}

AUTHORITY_SOURCE_ROLES = {
    'teacher_ppt',
    'textbook',
    'official_handout',
    'syllabus',
    'user_note',
}

QUESTION_SOURCE_ROLES = {
    'source_question',
    'historical_exam',
    'assignment_or_quiz',
}

SECONDARY_SOURCE_ROLES = {
    'senior_note',
    'existing_vault',
    'external_supplement',
    'model_inference_pending_verification',
    'unclassified_source',
}

ROLE_ORDER = {
    'teacher_ppt': 0,
    'textbook': 1,
    'official_handout': 2,
    'syllabus': 3,
    'user_note': 4,
    'source_question': 5,
    'historical_exam': 6,
    'assignment_or_quiz': 7,
    'senior_note': 8,
    'existing_vault': 9,
    'external_supplement': 10,
    'model_inference_pending_verification': 11,
    'unclassified_source': 12,
}

SOURCE_HINTS = [
    ('syllabus', 'syllabus'),
    ('exam_scope', 'syllabus'),
    ('大纲', 'syllabus'),
    ('考试范围', 'syllabus'),
    ('teacher_ppt', 'teacher_ppt'),
    ('teacher-ppt', 'teacher_ppt'),
    ('teacher', 'teacher_ppt'),
    ('slides', 'teacher_ppt'),
    ('slide', 'teacher_ppt'),
    ('pptx', 'teacher_ppt'),
    ('ppt', 'teacher_ppt'),
    ('lecture', 'teacher_ppt'),
    ('课件', 'teacher_ppt'),
    ('老师', 'teacher_ppt'),
    ('授课', 'teacher_ppt'),
    ('textbook', 'textbook'),
    ('coursebook', 'textbook'),
    ('教材', 'textbook'),
    ('蓝皮书', 'textbook'),
    ('official', 'official_handout'),
    ('handout', 'official_handout'),
    ('manual', 'official_handout'),
    ('standard', 'official_handout'),
    ('讲义', 'official_handout'),
    ('标准', 'official_handout'),
    ('手册', 'official_handout'),
    ('past_exam', 'historical_exam'),
    ('past-exam', 'historical_exam'),
    ('past', 'historical_exam'),
    ('exam', 'historical_exam'),
    ('midterm', 'historical_exam'),
    ('final', 'historical_exam'),
    ('历年', 'historical_exam'),
    ('真题', 'historical_exam'),
    ('考试', 'historical_exam'),
    ('试题', 'historical_exam'),
    ('homework', 'assignment_or_quiz'),
    ('assignment', 'assignment_or_quiz'),
    ('quiz', 'assignment_or_quiz'),
    ('作业', 'assignment_or_quiz'),
    ('测验', 'assignment_or_quiz'),
    ('小测', 'assignment_or_quiz'),
    ('question_bank', 'source_question'),
    ('question-bank', 'source_question'),
    ('review_question', 'source_question'),
    ('question', 'source_question'),
    ('exercise', 'source_question'),
    ('题库', 'source_question'),
    ('习题', 'source_question'),
    ('练习', 'source_question'),
    ('复习题', 'source_question'),
    ('思考题', 'source_question'),
    ('senior', 'senior_note'),
    ('学长', 'senior_note'),
    ('学姐', 'senior_note'),
    ('复习资料', 'senior_note'),
    ('user_note', 'user_note'),
    ('user-notes', 'user_note'),
    ('my_note', 'user_note'),
    ('class_note', 'user_note'),
    ('annotation', 'user_note'),
    ('课堂笔记', 'user_note'),
    ('笔记', 'user_note'),
    ('vault', 'existing_vault'),
    ('obsidian', 'existing_vault'),
    ('既有', 'existing_vault'),
    ('已有', 'existing_vault'),
    ('external', 'external_supplement'),
    ('supplement', 'external_supplement'),
    ('paper', 'external_supplement'),
    ('外部', 'external_supplement'),
    ('补充', 'external_supplement'),
]


def normalize_source_role(role: str | None) -> str:
    if not role:
        return 'unclassified_source'
    return LEGACY_SOURCE_ROLE_MAP.get(role, role)


def role_in(role: str | None, role_set: set[str]) -> bool:
    return normalize_source_role(role) in role_set


def role_rank(role: str | None) -> int:
    return ROLE_ORDER.get(normalize_source_role(role), 99)


def normalize_role_counts(role_counts: dict) -> dict:
    merged = {}
    for role, count in role_counts.items():
        normalized = normalize_source_role(role)
        merged[normalized] = merged.get(normalized, 0) + int(count or 0)
    return dict(sorted(merged.items()))


def infer_source_role(path: Path) -> str:
    parts = [str(part).lower() for part in path.parts[-4:]]
    haystack = ' '.join(parts).replace('\\', '/')
    for hint, role in SOURCE_HINTS:
        if hint.lower() in haystack:
            return role
    return 'unclassified_source'
