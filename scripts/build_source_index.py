#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from source_roles import infer_source_role

TEXT_EXTS = {'.md', '.txt', '.markdown'}
GENERATED_DIRS = {'.course_index', '_working', '期末复习'}
INDEX_VERSION = '4.4'
CORE_INDEX_FILES = ['files.jsonl', 'chunks.jsonl', 'headings.jsonl', 'questions.jsonl', 'terms.jsonl', 'progress.json']
QUESTION_HEADING_RE = re.compile(r'(复习题|课后习题|思考题|历年题|考试题|试题|题库|作业题|练习题|自测题|review questions?|exercises?|homework|quiz|exam)', re.I)
QUESTION_LINE_RE = re.compile(r'(^|\n)\s*(?:#{1,6}\s*)?(?:\d+[.、)]|[（(]\d+[）)]|Q\d+[:：]|题目[:：]|问题[:：]|问[:：]|简答题[:：]?|论述题[:：]?|判断题[:：]?|名词解释[:：]?|选择题[:：]?)\s*(.+)')
ANSWER_MARK_RE = re.compile(r'(答案|参考答案|解析|解答|答[:：]|analysis|answer)', re.I)
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
CHAPTER_RE = re.compile(r'(第\s*[一二三四五六七八九十百0-9]+\s*[章节篇]|chapter\s*\d+|ch\.?\s*\d+)', re.I)
TERM_RE = re.compile(r'[A-Za-z][A-Za-z0-9_/-]{1,}(?:模型|技术|方法|系统|算法|平台|流程|标准|协议|函数|定理|理论|结构|机制|规则|公式|概念|指标|工具|框架)|[A-Za-z][A-Za-z0-9_/-]{2,}|[一-鿿]{2,12}')
STOP_TERMS = {
    '老师', '重点', '注意', '已有答案', '章节', '资料', '复习', '检查', '本章', '全书', '内容', '问题', '答案', '解析',
    '定义', '概念', '方法', '过程', '特点', '作用', '意义', '原因', '影响', '应用', '类型', '分类', '原则', '什么是',
    'the', 'and', 'for', 'with', 'this', 'that', 'chapter', 'page', 'slide', 'section', 'figure', 'table'
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
    return 'good'


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
    seen = set()
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
            row = {
                'file': rel,
                'source_role': role,
                'question': question[:300],
                'heading_path': heading_path,
                'inferred_chapter': infer_chapter(question, heading_path),
                'question_type': question_type(question),
                'question_source_type': source_question_kind(path, heading_path),
                'has_answer': likely_has_answer(text, absolute),
            }
            seen.add((row['file'], row['question']))
            qrows.append(row)
    for qm in QUESTION_LINE_RE.finditer(text):
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
        if key not in seen:
            qrows.append(row)
            seen.add(key)
    return qrows


def write_jsonl(path: Path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return default


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def is_under_index(path: Path, out: Path) -> bool:
    try:
        path.relative_to(out)
        return True
    except ValueError:
        return False


def discover_sources(input_dir: Path, out: Path) -> list[Path]:
    sources = []
    for p in input_dir.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        rel_parts = p.relative_to(input_dir).parts
        if any(part in GENERATED_DIRS for part in rel_parts):
            continue
        if not is_under_index(p, out):
            sources.append(p)
    return sorted(sources)


def file_fingerprint(path: Path, input_dir: Path, include_hash=True) -> dict:
    stat = path.stat()
    row = {
        'file': path.relative_to(input_dir).as_posix(),
        'size': stat.st_size,
        'mtime_ns': stat.st_mtime_ns,
        'source_role': infer_source_role(path),
    }
    if include_hash:
        row['sha256'] = sha256_file(path)
    return row


def load_manifest(out: Path) -> dict[str, dict]:
    rows = read_jsonl(out / 'manifest.jsonl')
    return {row.get('file'): row for row in rows if row.get('file')}


def compute_delta(current_rows: list[dict], old_by_file: dict[str, dict]) -> dict:
    current_by_file = {row['file']: row for row in current_rows}
    added, changed, unchanged, deleted = [], [], [], []
    for rel, row in current_by_file.items():
        old = old_by_file.get(rel)
        if not old:
            added.append(rel)
            continue
        old_sig = (old.get('size'), old.get('mtime_ns'), old.get('source_role'))
        new_sig = (row.get('size'), row.get('mtime_ns'), row.get('source_role'))
        if old.get('sha256') is not None and row.get('sha256') is not None:
            old_sig = (*old_sig, old.get('sha256'))
            new_sig = (*new_sig, row.get('sha256'))
        if old_sig == new_sig:
            unchanged.append(rel)
        else:
            changed.append(rel)
    for rel in old_by_file:
        if rel not in current_by_file:
            deleted.append(rel)
    return {
        'added': sorted(added),
        'changed': sorted(changed),
        'unchanged': sorted(unchanged),
        'deleted': sorted(deleted),
    }


def core_files_present(out: Path) -> bool:
    return all((out / name).exists() for name in CORE_INDEX_FILES)


def build_rows(input_dir: Path, source_paths: list[Path]):
    files = []
    chunks = []
    headings = []
    questions = []
    term_stats = defaultdict(lambda: {'count': 0, 'files': set(), 'source_roles': defaultdict(int), 'chapters': defaultdict(int), 'chunks': set()})
    chunk_num = 0

    for path in source_paths:
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
    return files, chunks, headings, questions, terms


def assign_file_ids(files: list[dict]) -> list[dict]:
    rows = []
    for idx, row in enumerate(sorted(files, key=lambda r: r.get('file') or ''), 1):
        item = dict(row)
        item['file_id'] = f'f{idx}'
        rows.append(item)
    return rows


def assign_chunk_ids_and_terms(chunks: list[dict]) -> tuple[list[dict], list[dict]]:
    term_stats = defaultdict(lambda: {'count': 0, 'files': set(), 'source_roles': defaultdict(int), 'chapters': defaultdict(int), 'chunks': set()})
    normalized = []
    for idx, row in enumerate(sorted(chunks, key=lambda r: (r.get('file') or '', r.get('chunk_id') or '')), 1):
        item = dict(row)
        cid = f'c{idx}'
        item['chunk_id'] = cid
        normalized.append(item)
        chapter = item.get('inferred_chapter') or ''
        for raw in TERM_RE.findall(item.get('text') or ''):
            term = normalize_term(raw)
            if should_keep_term(term):
                st = term_stats[term]
                st['count'] += 1
                st['files'].add(item.get('file'))
                st['source_roles'][item.get('source_role')] += 1
                if chapter:
                    st['chapters'][chapter] += 1
                st['chunks'].add(cid)

    terms = []
    for term, st in term_stats.items():
        terms.append({
            'term': term,
            'count': st['count'],
            'files': sorted(f for f in st['files'] if f),
            'source_roles': dict(sorted((k, v) for k, v in st['source_roles'].items() if k)),
            'chapters': dict(sorted(st['chapters'].items())),
            'chunks': sorted(st['chunks']),
        })
    terms.sort(key=lambda r: (-r['count'], -len(r['source_roles']), r['term']))
    return normalized, terms[:3000]


def merge_updated_rows(out: Path, input_dir: Path, source_paths: list[Path], delta: dict):
    impacted = set(delta['added'] + delta['changed'] + delta['deleted'])
    changed_paths = [path for path in source_paths if path.relative_to(input_dir).as_posix() in set(delta['added'] + delta['changed'])]
    new_files, new_chunks, new_headings, new_questions, _ = build_rows(input_dir, changed_paths)

    old_files = [row for row in read_jsonl(out / 'files.jsonl') if row.get('file') not in impacted]
    old_chunks = [row for row in read_jsonl(out / 'chunks.jsonl') if row.get('file') not in impacted]
    old_headings = [row for row in read_jsonl(out / 'headings.jsonl') if row.get('file') not in impacted]
    old_questions = [row for row in read_jsonl(out / 'questions.jsonl') if row.get('file') not in impacted]

    files = assign_file_ids(old_files + new_files)
    chunks, terms = assign_chunk_ids_and_terms(old_chunks + new_chunks)
    headings = sorted(old_headings + new_headings, key=lambda r: (r.get('file') or '', r.get('offset') or 0))
    questions = sorted(old_questions + new_questions, key=lambda r: (r.get('file') or '', r.get('question') or ''))
    return files, chunks, headings, questions, terms


def build_or_merge_rows(out: Path, input_dir: Path, source_paths: list[Path], action: str, delta: dict):
    if action == 'update':
        return merge_updated_rows(out, input_dir, source_paths, delta)
    return build_rows(input_dir, source_paths)


def impacted_chapters(chunks: list[dict], impacted_files: set[str]) -> list[str]:
    chapters = {row.get('inferred_chapter') for row in chunks if row.get('file') in impacted_files and row.get('inferred_chapter')}
    return sorted(chapters)


def extraction_quality_warnings(files: list[dict]) -> list[str]:
    counts = defaultdict(int)
    for row in files:
        counts[row.get('extraction_quality') or 'uncertain'] += 1
    flagged = {key: counts[key] for key in ('poor', 'empty', 'image_only', 'uncertain') if counts.get(key)}
    if not flagged:
        return []
    detail = ', '.join(f'{key}={value}' for key, value in flagged.items())
    return [f'extraction quality needs review: {detail}']


def make_health(out: Path, input_dir: Path, action: str, delta: dict, counts: dict, current_rows: list[dict], warnings: list[str]) -> dict:
    old_progress = read_json(out / 'progress.json', {}) or {}
    old_files = old_progress.get('files')
    if old_files and counts['files'] < max(1, old_files // 2):
        warnings.append(f"large shrink detected: previous files={old_files}, current files={counts['files']}")
    if counts['files'] > 0 and counts['chunks'] < counts['files']:
        warnings.append('chunk count is lower than file count; extraction may be incomplete')
    if any(row.get('size') == 0 for row in current_rows):
        warnings.append('one or more source files are empty')
    missing = [name for name in CORE_INDEX_FILES if not (out / name).exists()]
    if action in {'rebuild', 'update', 'noop'}:
        missing = []
    if missing:
        warnings.append('missing core index files: ' + ', '.join(missing))
    status = 'ok' if not warnings else 'needs_review'
    return {
        'version': INDEX_VERSION,
        'status': status,
        'index_action': action,
        'input_dir': str(input_dir),
        'index_dir': str(out),
        'checked_at': now_iso(),
        'counts': counts,
        'delta': {key: len(value) for key, value in delta.items()},
        'warnings': warnings,
    }


def write_index(out: Path, files, chunks, headings, questions, terms, progress: dict, manifest_rows: list[dict], health: dict):
    write_jsonl(out / 'files.jsonl', files)
    write_jsonl(out / 'chunks.jsonl', chunks)
    write_jsonl(out / 'headings.jsonl', headings)
    write_jsonl(out / 'questions.jsonl', questions)
    write_jsonl(out / 'terms.jsonl', terms)
    write_jsonl(out / 'manifest.jsonl', manifest_rows)
    (out / 'progress.json').write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'health.json').write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding='utf-8')


def print_status(out: Path, input_dir: Path):
    progress = read_json(out / 'progress.json', {}) or {}
    health = read_json(out / 'health.json', {}) or {}
    manifest = read_jsonl(out / 'manifest.jsonl')
    current_paths = discover_sources(input_dir, out) if input_dir.exists() else []
    current_rows = [file_fingerprint(path, input_dir, include_hash=False) for path in current_paths]
    delta = compute_delta(current_rows, {row.get('file'): row for row in manifest if row.get('file')}) if manifest else {'added': [], 'changed': [], 'unchanged': [], 'deleted': []}
    print(json.dumps({
        'index_dir': str(out),
        'input_dir': str(input_dir),
        'status': health.get('status', 'unknown'),
        'version': progress.get('version'),
        'last_indexed_at': progress.get('indexed_at'),
        'files': progress.get('files', 0),
        'chunks': progress.get('chunks', 0),
        'questions': progress.get('questions', 0),
        'terms': progress.get('terms', 0),
        'pending_delta': {key: len(value) for key, value in delta.items()},
        'warnings': health.get('warnings', []),
        'core_files_present': core_files_present(out),
    }, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description='Build or update a lightweight course source index from extracted text/markdown.')
    ap.add_argument('input_dir')
    ap.add_argument('--out', default=None, help='Output index directory, default: INPUT/.course_index')
    ap.add_argument('--force', action='store_true', help='Rebuild even when the manifest says sources are unchanged.')
    ap.add_argument('--status', action='store_true', help='Print index status/delta without rebuilding.')
    ap.add_argument('--no-hash', action='store_true', help='Use size/mtime/source_role only for faster change detection.')
    args = ap.parse_args()
    input_dir = Path(args.input_dir)
    out = Path(args.out) if args.out else input_dir / '.course_index'
    out.mkdir(parents=True, exist_ok=True)

    if args.status:
        print_status(out, input_dir)
        return

    source_paths = discover_sources(input_dir, out)
    current_manifest = [file_fingerprint(path, input_dir, include_hash=not args.no_hash) for path in source_paths]
    old_manifest = load_manifest(out)
    delta = compute_delta(current_manifest, old_manifest)
    has_existing_index = core_files_present(out) and bool(old_manifest)
    has_changes = bool(delta['added'] or delta['changed'] or delta['deleted'])
    action = 'rebuild'
    if has_existing_index and not args.force:
        action = 'update' if has_changes else 'noop'
    elif has_existing_index and args.force:
        action = 'rebuild'

    if action == 'noop':
        progress = read_json(out / 'progress.json', {}) or {}
        existing_files = read_jsonl(out / 'files.jsonl')
        counts = {
            'files': progress.get('files', len(current_manifest)),
            'chunks': progress.get('chunks', 0),
            'questions': progress.get('questions', 0),
            'terms': progress.get('terms', 0),
        }
        health = make_health(out, input_dir, action, delta, counts, current_manifest, extraction_quality_warnings(existing_files))
        (out / 'health.json').write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({
            'index_dir': str(out),
            'index_action': action,
            'status': health['status'],
            **counts,
            'delta': health['delta'],
            'warnings': health['warnings'],
        }, ensure_ascii=False))
        return

    files, chunks, headings, questions, terms = build_or_merge_rows(out, input_dir, source_paths, action, delta)
    impacted = set(delta['added'] + delta['changed'] + delta['deleted'])
    counts = {'files': len(files), 'chunks': len(chunks), 'questions': len(questions), 'terms': len(terms)}
    health = make_health(out, input_dir, action, delta, counts, current_manifest, extraction_quality_warnings(files))
    progress = {
        'version': INDEX_VERSION,
        'input_dir': str(input_dir),
        'index_dir': str(out),
        'indexed_at': health['checked_at'],
        **counts,
        'index_action': action,
        'delta': health['delta'],
        'impacted_chapters': impacted_chapters(chunks, impacted),
    }
    write_index(out, files, chunks, headings, questions, terms, progress, current_manifest, health)
    print(json.dumps({
        'index_dir': str(out),
        'index_action': action,
        'status': health['status'],
        **counts,
        'delta': health['delta'],
        'impacted_chapters': progress['impacted_chapters'],
        'warnings': health['warnings'],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
