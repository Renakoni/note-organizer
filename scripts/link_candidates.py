#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from collections import Counter
from source_roles import QUESTION_SOURCE_ROLES, normalize_role_counts

STOP_TERMS = {
    '老师', '重点', '注意', '已有答案', '章节', '资料', '复习', '检查', '本章', '全书', '内容', '问题', '答案', '解析',
    '定义', '概念', '方法', '过程', '特点', '作用', '意义', '原因', '影响', '应用', '类型', '分类', '原则',
    '第一章', '第二章', '第三章', '第四章', '第五章', '第六章', '什么是'
}
SECTION_LABELS = {
    '概述', '背景', '定义', '原理', '方法', '过程', '步骤', '分类', '特点', '作用', '意义', '应用', '案例',
    '表现', '检查', '诊断', '治疗', '处理', '评价', '结果', '讨论', '总结', '练习', '思考题',
    '复习题', '自测', '课堂笔记', '临床表现', '辅助检查', '治疗原则'
}
GENERIC_PREFIX_RE = re.compile(r'^(不要|主要|包括|进行|判断|比较|简述|说明|如何|为什么|哪些|一种以|通常|相关|有关|仍|与|的|本|该|其|由|将|可|应|要)')
BAD_PHRASE_RE = re.compile(r'(包括|原则|依据|支持|有关|通常|一种以|表现为|由于|因此|所以|通过|进行|需要|可以|应当|必须|降低|升高|增加|减少|导致|用于|作为|重点|时|和|与|或)')
MARKER_RE = re.compile(r'^(老师说|老师强调|存疑|不会|待确认|必考|考过|易错|重点|注意)$')


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def clean_link(term: str) -> str:
    term = term.strip().strip('.,;:：，。；、（）()[]【】')
    term = re.sub(r'\s+', '', term) if re.search(r'[一-鿿]', term) else re.sub(r'\s+', '_', term)
    return term


def looks_like_sentence(t: str) -> bool:
    if re.search(r'[A-Za-z/]', t):
        return False
    if len(t) >= 5 and BAD_PHRASE_RE.search(t):
        return True
    if len(t) >= 12 and re.search(r'(是|为|有|在|和|或|及|与)', t):
        return True
    return False


def good_term(term: str) -> bool:
    t = clean_link(term)
    if len(t) < 2 or t in STOP_TERMS or t in SECTION_LABELS or t.lower() in STOP_TERMS:
        return False
    if re.fullmatch(r'\d+', t):
        return False
    if MARKER_RE.fullmatch(t):
        return False
    if len(t) > 18 and not re.search(r'[A-Za-z/]', t):
        return False
    if GENERIC_PREFIX_RE.search(t):
        return False
    if looks_like_sentence(t):
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description='Suggest Obsidian wikilink candidates from a course index or chapter pack.')
    ap.add_argument('index_dir')
    ap.add_argument('--chapter', default='')
    ap.add_argument('--limit', type=int, default=30)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    index_dir = Path(args.index_dir)
    terms = read_jsonl(index_dir / 'terms.jsonl')
    chunks = read_jsonl(index_dir / 'chunks.jsonl')
    questions = read_jsonl(index_dir / 'questions.jsonl')
    chapter = args.chapter.lower()

    chapter_chunk_ids = set()
    if chapter:
        for c in chunks:
            hay = ' '.join([c.get('inferred_chapter') or '', ' / '.join(c.get('heading_path') or []), c.get('text', '')[:400]]).lower()
            if chapter in hay:
                chapter_chunk_ids.add(c.get('chunk_id'))

    scores = Counter()
    evidence = {}
    for row in terms:
        term = clean_link(row.get('term', ''))
        if not good_term(term):
            continue
        row_chunks = set(row.get('chunks') or [])
        if chapter and not (row_chunks & chapter_chunk_ids or chapter in json.dumps(row.get('chapters', {}), ensure_ascii=False).lower()):
            continue
        score = row.get('count', 0)
        roles = normalize_role_counts(row.get('source_roles') or {})
        score += 3 * int(bool({'teacher_ppt', 'textbook', 'official_handout', 'syllabus'} & set(roles)))
        score += 2 * int('user_note' in roles)
        score += 2 * int(bool(QUESTION_SOURCE_ROLES & set(roles)))
        if re.search(r'[A-Za-z/]', term):
            score += 2
        scores[term] += score
        evidence.setdefault(term, {'files': row.get('files', []), 'source_roles': roles, 'count': row.get('count', 0)})

    for q in questions:
        qtext = q.get('question', '')
        for term in list(scores):
            if term in qtext:
                scores[term] += 4
                evidence[term]['question_hit'] = True

    ranked = [t for t, _ in scores.most_common(args.limit)]
    rows = [{'link': f'[[{t}]]', 'term': t, 'score': scores[t], 'evidence': evidence.get(t, {})} for t in ranked]
    if args.json:
        output = json.dumps({'links': rows}, ensure_ascii=False, indent=2) + '\n'
    else:
        lines = ['# Wikilink candidates', '']
        for row in rows:
            roles = ', '.join(row['evidence'].get('source_roles', {}).keys())
            lines.append(f"- {row['link']} — score {row['score']} ({roles})")
        output = '\n'.join(lines) + '\n'
    if args.out:
        Path(args.out).write_text(output, encoding='utf-8')
    print(output)

if __name__ == '__main__':
    main()
