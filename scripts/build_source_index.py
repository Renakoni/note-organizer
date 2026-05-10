#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from collections import defaultdict

TEXT_EXTS = {'.md', '.txt', '.markdown'}
SOURCE_HINTS = [
    ('teacher', 'teacher/textbook'), ('ppt', 'teacher/textbook'), ('lecture', 'teacher/textbook'),
    ('教材', 'teacher/textbook'), ('老师', 'teacher/textbook'), ('课件', 'teacher/textbook'),
    ('textbook', 'teacher/textbook'), ('book', 'teacher/textbook'), ('manual', 'teacher/textbook'), ('handout', 'teacher/textbook'),
    ('蓝皮书', 'teacher/textbook'), ('讲义', 'teacher/textbook'),
    ('user', 'user_notes'), ('note', 'user_notes'), ('课堂', 'user_notes'), ('笔记', 'user_notes'),
    ('past', 'historical_questions'), ('question', 'historical_questions'), ('exam', 'historical_questions'),
    ('往年', 'historical_questions'), ('题库', 'historical_questions'), ('试题', 'historical_questions'), ('习题', 'historical_questions'),
    ('senior', 'senior_notes'), ('学长', 'senior_notes'), ('复习资料', 'senior_notes'),
]
QUESTION_HEADING_RE = re.compile(r'(复习题|课后习题|思考题|历年题|考试题|试题|题库|作业题|练习题|自测题|review questions?|exercises?|homework|quiz|exam)', re.I)
QUESTION_LINE_RE = re.compile(r'(^|\n)\s*(?:#{1,6}\s*)?(?:\d+[.、)]|[（(]\d+[）)]|Q\d+[:：]|题目[:：]|问题[:：]|问[:：]|简答题[:：]?|论述题[:：]?|判断题[:：]?|名词解释[:：]?|选择题[:：]?)\s*(.+)')
ANSWER_MARK_RE = re.compile(r'(答案|参考答案|解析|解答|答[:：]|analysis|answer)', re.I)
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
CHAPTER_RE = re.compile(r'(第\s*[一二三四五六七八九十百0-9]+\s*[章节篇]|chapter\s*\d+|ch\.?\s*\d+)', re.I)
TERM_RE = re.compile(r'[A-Za-z][A-Za-z0-9_/-]{2,}|[一-鿿]{2,12}')
STOP_TERMS = {
    '老师', '重点', '注意', '已有答案', '章节', '资料', '复习', '检查', '本章', '全书', '内容', '问题', '答案', '解析',
    '定义', '概念', '方法', '过程', '特点', '作用', '意义', '原因', '影响', '应用', '类型', '分类', '原则',
    'the', 'and', 'for', 'with', 'this', 'that', 'chapter', 'page', 'slide', 'section', 'figure', 'table'
}


def infer_source_role(path: Path) -> str:
    name = str(path).lower()
    for hint, role in SOURCE_HINTS:
        if hint.lower() in name:
            return role
    return 'other'


def infer_chapter(text: str, heading_path: list[str]) -> str:
    hay = ' / '.join(heading_path) + '\n' + text[:500]
    m = CHAPTER_RE.search(hay)
    return re.sub(r'\s+', '', m.group(0)) if m else ''


def extraction_quality(text: str) -> str:
    if not text.strip():
        return 'empty'
    bad = text.count('�') + text.count('�')
    if bad > 5 or len(text.strip()) < 30:
        return 'poor'
    return 'ok'


def split_chunks(text: str) -> list[tuple[list[str], str]]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        chunks = []
        buf = []
        for para in paras:
            buf.append(para)
            if sum(len(x) for x in buf) > 1200:
                chunks.append(([], '\n\n'.join(buf)))
                buf = []
        if buf:
            chunks.append(([], '\n\n'.join(buf)))
        return chunks or [([], text.strip())]

    chunks = []
    stack = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        while len(stack) >= level:
            stack.pop()
        stack.append(title)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        chunk_text = (m.group(0).strip() + ('\n' + body if body else '')).strip()
        if chunk_text:
            chunks.append((stack.copy(), chunk_text))
    return chunks


def page_or_slide(path: Path, heading_path: list[str], text: str) -> str:
    hay = ' '.join(heading_path) + ' ' + text[:80]
    m = re.search(r'(?:page|slide|第)\s*([0-9一二三四五六七八九十]+)\s*(?:页|张|slide)?', hay, re.I)
    return m.group(0) if m else ''


def normalize_term(term: str) -> str:
    return term.strip().strip('.,;:：，。；、（）()[]【】')


def should_keep_term(term: str) -> bool:
    t = normalize_term(term)
    if len(t) < 2 or t.lower() in STOP_TERMS:
        return False
    if re.fullmatch(r'\d+', t):
        return False
    return True


def question_type(text: str) -> str:
    checks = [
        ('名词解释', '名词解释'), ('选择', '选择题'), ('判断', '判断题'), ('简答', '简答题'),
        ('论述', '论述题'), ('计算', '计算题'), ('推导', '推导题'), ('比较', '对比题'),
        ('case', '案例题'), ('案例', '案例题')
    ]
    lower = text.lower()
    for key, label in checks:
        if key.lower() in lower:
            return label
    if text.endswith(('？', '?')) or re.search(r'(什么|为什么|如何|怎样|哪些|是否|区别)', text):
        return '问答题'
    return '未分类'


def source_question_kind(path: Path, heading_path: list[str]) -> str:
    hay = (path.name + ' ' + ' / '.join(heading_path)).lower()
    if re.search(r'(past|exam|历年|考试|试题)', hay):
        return '历年/考试题'
    if re.search(r'(homework|assignment|作业)', hay):
        return '作业题'
    if re.search(r'(课后|习题|练习|exercise)', hay):
        return '课后/练习题'
    if re.search(r'(review|复习|思考)', hay):
        return '复习/思考题'
    if re.search(r'(题库|question)', hay):
        return '题库'
    return '来源题'


def likely_has_answer(text: str, start: int, next_start: int | None = None) -> bool:
    window = text[start:next_start or min(len(text), start + 900)]
    return bool(ANSWER_MARK_RE.search(window))


def heading_path_before(text: str, offset: int) -> list[str]:
    stack = []
    for hm in HEADING_RE.finditer(text[:offset]):
        level = len(hm.group(1))
        title = hm.group(2).strip()
        while len(stack) >= level:
            stack.pop()
        stack.append(title)
    return stack


def extract_questions(text: str, path: Path, rel: str, role: str) -> list[dict]:
    heading_matches = list(HEADING_RE.finditer(text))
    qrows = []
    for i, m in enumerate(heading_matches):
        title = m.group(2).strip()
        if not QUESTION_HEADING_RE.search(title):
            continue
        start = m.end()
        end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(text)
        section = text[start:end]
        heading_path = heading_path_before(text, m.start()) + [title]
        for qm in QUESTION_LINE_RE.finditer('\n' + section):
            question = qm.group(2).strip()
            if len(question) < 2:
                continue
            absolute = start + max(0, qm.start(2) - 1)
            qrows.append({
                'file': rel,
                'source_role': role,
                'question': question[:300],
                'heading_path': heading_path,
                'inferred_chapter': infer_chapter(question, heading_path),
                'question_type': question_type(question),
                'question_source_type': source_question_kind(path, heading_path),
                'has_answer': likely_has_answer(text, absolute),
            })
    for idx, qm in enumerate(QUESTION_LINE_RE.finditer(text)):
        question = qm.group(2).strip()
        if len(question) < 2 or len(question) > 300:
            continue
        prefix = text[max(0, qm.start() - 400):qm.start()]
        headings = heading_path_before(text, qm.start())[-4:]
        if not headings and not QUESTION_HEADING_RE.search(prefix[-120:] + question):
            continue
        next_q = QUESTION_LINE_RE.search(text, qm.end())
        next_start = next_q.start() if next_q else None
        row = {
            'file': rel,
            'source_role': role,
            'question': question[:300],
            'heading_path': headings,
            'inferred_chapter': infer_chapter(question, headings),
            'question_type': question_type(question),
            'question_source_type': source_question_kind(path, headings),
            'has_answer': likely_has_answer(text, qm.end(), next_start),
        }
        key = (row['file'], row['question'])
        if key not in {(r['file'], r['question']) for r in qrows}:
            qrows.append(row)
    return qrows


def write_jsonl(path: Path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser(description='Build a lightweight course source index from extracted text/markdown.')
    ap.add_argument('input_dir')
    ap.add_argument('--out', default=None, help='Output index directory, default: INPUT/.course_index')
    args = ap.parse_args()
    input_dir = Path(args.input_dir)
    out = Path(args.out) if args.out else input_dir / '.course_index'
    out.mkdir(parents=True, exist_ok=True)

    files = []
    chunks = []
    headings = []
    questions = []
    term_stats = defaultdict(lambda: {'count': 0, 'files': set(), 'source_roles': defaultdict(int), 'chapters': defaultdict(int), 'chunks': set()})
    chunk_num = 0

    for path in sorted(p for p in input_dir.rglob('*') if p.is_file() and p.suffix.lower() in TEXT_EXTS and '.course_index' not in p.parts):
        text = path.read_text(encoding='utf-8', errors='replace')
        role = infer_source_role(path)
        quality = extraction_quality(text)
        rel = path.relative_to(input_dir).as_posix()
        file_id = f'f{len(files)+1}'
        files.append({'file_id': file_id, 'file': rel, 'source_role': role, 'chars': len(text), 'extraction_quality': quality})

        for hm in HEADING_RE.finditer(text):
            headings.append({'file': rel, 'level': len(hm.group(1)), 'heading': hm.group(2).strip(), 'offset': hm.start()})

        for heading_path, chunk_text in split_chunks(text):
            chunk_num += 1
            cid = f'c{chunk_num}'
            chapter = infer_chapter(chunk_text, heading_path)
            chunks.append({
                'chunk_id': cid,
                'file': rel,
                'source_role': role,
                'page_or_slide': page_or_slide(path, heading_path, chunk_text),
                'heading_path': heading_path,
                'text': chunk_text,
                'extraction_quality': quality,
                'inferred_chapter': chapter,
            })
            for raw in TERM_RE.findall(chunk_text):
                term = normalize_term(raw)
                if should_keep_term(term):
                    st = term_stats[term]
                    st['count'] += 1
                    st['files'].add(rel)
                    st['source_roles'][role] += 1
                    if chapter:
                        st['chapters'][chapter] += 1
                    st['chunks'].add(cid)

        questions.extend(extract_questions(text, path, rel, role))

    terms = []
    for term, st in term_stats.items():
        terms.append({
            'term': term,
            'count': st['count'],
            'files': sorted(st['files']),
            'source_roles': dict(sorted(st['source_roles'].items())),
            'chapters': dict(sorted(st['chapters'].items())),
            'chunks': sorted(st['chunks']),
        })
    terms.sort(key=lambda r: (-r['count'], -len(r['source_roles']), r['term']))
    terms = terms[:3000]

    write_jsonl(out / 'files.jsonl', files)
    write_jsonl(out / 'chunks.jsonl', chunks)
    write_jsonl(out / 'headings.jsonl', headings)
    write_jsonl(out / 'questions.jsonl', questions)
    write_jsonl(out / 'terms.jsonl', terms)
    (out / 'progress.json').write_text(json.dumps({'version': '4.2', 'input_dir': str(input_dir), 'files': len(files), 'chunks': len(chunks), 'questions': len(questions), 'terms': len(terms)}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'index_dir': str(out), 'files': len(files), 'chunks': len(chunks), 'questions': len(questions), 'terms': len(terms)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
