#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

TERM_RE = re.compile(r'[A-Za-z][A-Za-z0-9_-]{2,}|[一-鿿]{2,12}')


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def extract_items(text):
    items = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r'^(#{1,6}\s+|\d+[.、)]\s+|[-*]\s+|\|)', s):
            clean = re.sub(r'[#|*_`]', '', s).strip()
            terms = [t for t in TERM_RE.findall(clean) if len(t) >= 2]
            if terms:
                items.append({'text': clean[:300], 'terms': terms[:12]})
    if not items:
        terms = [t for t in TERM_RE.findall(text) if len(t) >= 2]
        if terms:
            items.append({'text': text[:300], 'terms': terms[:12]})
    return items[:200]


def support_for(terms, chunks):
    hits = []
    for row in chunks:
        hay = row.get('text', '')
        count = sum(1 for t in terms if t and t in hay)
        if count:
            hits.append({'count': count, 'file': row.get('file'), 'chunk_id': row.get('chunk_id'), 'source_role': row.get('source_role'), 'heading_path': row.get('heading_path'), 'snippet': re.sub(r'\s+', ' ', hay)[:220]})
    hits.sort(key=lambda h: (-h['count'], h['file'] or ''))
    return hits[:5]


def classify(item, hits):
    if not hits:
        return 'D'
    roles = {h.get('source_role') for h in hits}
    if 'teacher/textbook' in roles or 'user_notes' in roles:
        if hits[0]['count'] >= max(2, min(4, len(item['terms']) // 2)):
            return 'A'
        return 'B'
    if 'senior_notes' in roles or 'other' in roles:
        return 'C'
    return 'B'


def strengthening_action(coverage):
    return {
        'A': '链接对应笔记或来源，无需大改',
        'B': '把更完整的答题框架补入章节笔记或典型考法',
        'C': '确认外部补充已标记，不能覆盖本地权威材料',
        'D': '回查本地来源；无法确认则写入资料缺口与待确认',
    }.get(coverage, '人工复核')


def main():
    ap = argparse.ArgumentParser(description='Conservatively classify note/question support against a course index.')
    ap.add_argument('index_dir')
    ap.add_argument('input_markdown')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--strengthening-log', action='store_true', help='Emit table columns suitable for 00_题目覆盖与笔记补强.md')
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    chunks = read_jsonl(Path(args.index_dir) / 'chunks.jsonl')
    text = Path(args.input_markdown).read_text(encoding='utf-8', errors='replace')
    rows = []
    for item in extract_items(text):
        hits = support_for(item['terms'], chunks)
        cov = classify(item, hits)
        rows.append({'item': item['text'], 'terms': item['terms'], 'coverage': cov, 'required_action': strengthening_action(cov), 'hits': hits})

    if args.json:
        output = json.dumps({'items': rows}, ensure_ascii=False, indent=2)
    elif args.strengthening_log:
        lines = ['# 题目覆盖与笔记补强', '', '| 题目 | 覆盖类型 | 暴露问题 | 已补强到 | 仍需确认 |', '|---|---|---|---|---|']
        for row in rows:
            ev = '; '.join(f"{h['file']}:{h['chunk_id']}" for h in row['hits'][:3]) or 'No source hit'
            item = row['item'].replace('|', '/')
            lines.append(f"| {item} | {row['coverage']} | {row['required_action']} | {ev} | {'无' if row['coverage'] == 'A' else '需复核'} |")
        output = '\n'.join(lines) + '\n'
    else:
        lines = ['# Coverage check', '', '| Item | Coverage | Evidence | Required action |', '|---|---|---|---|']
        for row in rows:
            ev = '; '.join(f"{h['file']}:{h['chunk_id']}" for h in row['hits'][:3]) or 'No source hit'
            item = row['item'].replace('|', '/')
            lines.append(f"| {item} | {row['coverage']} | {ev} | {row['required_action']} |")
        output = '\n'.join(lines) + '\n'
    if args.out:
        Path(args.out).write_text(output, encoding='utf-8')
    print(output)

if __name__ == '__main__':
    main()
