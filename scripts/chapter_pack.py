#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from collections import Counter
from source_roles import AUTHORITY_SOURCE_ROLES, role_in, role_rank

TERM_RE = re.compile(r'[A-Za-z][A-Za-z0-9_/-]{1,}(?:模型|技术|方法|系统|算法|平台|流程|标准|协议|函数|定理|理论|结构|机制|规则|公式|概念|指标|工具|框架)|[A-Za-z][A-Za-z0-9_/-]{2,}|[一-鿿]{2,12}')
STOP_TERMS = {'老师', '重点', '注意', '已有答案', '章节', '资料', '复习', '检查', '本章', '全书', '内容', '问题', '答案', '解析', '定义', '概念', '方法', '过程', '特点', '作用', '意义', '原因', '影响', '应用', '类型', '分类', '原则', '什么是', 'the', 'and', 'for', 'with', 'this', 'that', 'chapter', 'page', 'slide'}


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def normalize_term(term: str) -> str:
    return term.strip().strip('.,;:：，。；、（）()[]【】')


def keep_term(term: str) -> bool:
    t = normalize_term(term)
    if len(t) < 2 or t.lower() in STOP_TERMS:
        return False
    if re.fullmatch(r'\d+', t):
        return False
    return True


def match_chapter(row, chapter):
    c = chapter.lower()
    hay = ' '.join([row.get('inferred_chapter') or '', ' / '.join(row.get('heading_path') or []), row.get('text', '')[:300]]).lower()
    return c in hay


def emphasis_hits(text):
    markers = ['老师说', '老师强调', '重点', '必考', '考过', '注意', '不会', '没懂', '存疑', '待确认', '?', '？']
    return [m for m in markers if m in text]


def extract_terms(rows, limit=24):
    counts = Counter()
    role_bonus = Counter()
    for r in rows:
        text = ' / '.join(r.get('heading_path') or []) + '\n' + r.get('text', '')
        for raw in TERM_RE.findall(text):
            term = normalize_term(raw)
            if keep_term(term):
                counts[term] += 1
                if role_in(r.get('source_role'), AUTHORITY_SOURCE_ROLES):
                    role_bonus[term] += 2
    ranked = sorted(counts, key=lambda t: (-(counts[t] + role_bonus[t]), -len(t), t))
    return ranked[:limit]


def question_score(question, terms):
    qtext = question.get('question', '')
    score = 0
    matched = []
    for term in terms:
        if term and term in qtext:
            score += 2 if re.search(r'[A-Za-z]', term) else 1
            matched.append(term)
    return score, matched


def main():
    ap = argparse.ArgumentParser(description='Build a compact chapter context pack from a course index.')
    ap.add_argument('index_dir')
    ap.add_argument('chapter')
    ap.add_argument('--limit', type=int, default=24)
    ap.add_argument('--question-limit', type=int, default=20)
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    index_dir = Path(args.index_dir)
    chunks = read_jsonl(index_dir / 'chunks.jsonl')
    questions = read_jsonl(index_dir / 'questions.jsonl')
    matched = [r for r in chunks if match_chapter(r, args.chapter)]
    if not matched:
        q = re.sub(r'第|章|chapter|ch\.?', '', args.chapter, flags=re.I).strip()
        matched = [r for r in chunks if q and q.lower() in r.get('text', '').lower()]

    matched.sort(key=lambda r: (role_rank(r.get('source_role')), r.get('file') or '', r.get('chunk_id') or ''))
    matched = matched[:args.limit]

    chapter_terms = extract_terms(matched)
    qhits = []
    for q in questions:
        direct = args.chapter.lower() in (q.get('question', '') + q.get('file', '')).lower()
        score, matched_terms = question_score(q, chapter_terms)
        if direct or score:
            qhits.append({'question': q, 'score': score + (5 if direct else 0), 'matched_terms': matched_terms})
    qhits.sort(key=lambda h: (-h['score'], h['question'].get('file') or '', h['question'].get('question') or ''))

    uncertainties = []
    for r in matched:
        marks = emphasis_hits(r.get('text', ''))
        if marks:
            uncertainties.append({'chunk_id': r.get('chunk_id'), 'file': r.get('file'), 'markers': marks, 'snippet': re.sub(r'\s+', ' ', r.get('text', ''))[:240]})

    lines = [f'# Chapter pack: {args.chapter}', '']
    lines.append('## Chapter term candidates')
    if chapter_terms:
        lines.append(', '.join(chapter_terms[:24]))
    else:
        lines.append('No term candidates found.')

    lines.append('\n## Source chunks')
    for r in matched:
        heading = ' / '.join(r.get('heading_path') or [])
        lines.append(f"\n### {r.get('chunk_id')} — {r.get('file')} ({r.get('source_role')})")
        if heading:
            lines.append(f"- heading: {heading}")
        if r.get('page_or_slide'):
            lines.append(f"- page/slide: {r.get('page_or_slide')}")
        lines.append('')
        lines.append(r.get('text', '')[:1600])
    lines.append('\n## Question hits')
    if qhits:
        for hit in qhits[:args.question_limit]:
            q = hit['question']
            terms = ', '.join(hit['matched_terms'][:8]) or 'direct chapter match'
            lines.append(f"- {q.get('file')}: {q.get('question')} (matched: {terms})")
    else:
        lines.append('- No question hits found by chapter name or chapter terms.')
    lines.append('\n## Emphasis and uncertainty markers')
    if uncertainties:
        for u in uncertainties[:20]:
            lines.append(f"- {u['file']} {u['chunk_id']} markers={','.join(u['markers'])}: {u['snippet']}")
    else:
        lines.append('- No emphasis/uncertainty markers found in selected chunks.')

    output = '\n'.join(lines).strip() + '\n'
    if args.out:
        Path(args.out).write_text(output, encoding='utf-8')
    print(output)

if __name__ == '__main__':
    main()
