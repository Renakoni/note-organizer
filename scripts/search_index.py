#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def score(row, pattern, regex=False, chapter=''):
    text = row.get('text', '')
    heading = ' / '.join(row.get('heading_path') or [])
    hay = heading + '\n' + text
    if regex:
        matches = re.findall(pattern, hay, re.I)
        base = len(matches)
    else:
        p = pattern.lower()
        base = hay.lower().count(p)
    if base == 0:
        return 0
    boost = 0
    if pattern.lower() in heading.lower():
        boost += 5
    if row.get('source_role') in {'teacher/textbook', 'user_notes'}:
        boost += 2
    if chapter and chapter.lower() in (row.get('inferred_chapter') or '').lower():
        boost += 3
    return base + boost


def main():
    ap = argparse.ArgumentParser(description='Search a lightweight course source index.')
    ap.add_argument('index_dir')
    ap.add_argument('query')
    ap.add_argument('--regex', action='store_true')
    ap.add_argument('--chapter', default='')
    ap.add_argument('--limit', type=int, default=10)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    index_dir = Path(args.index_dir)
    rows = read_jsonl(index_dir / 'chunks.jsonl')
    hits = []
    for row in rows:
        s = score(row, args.query, args.regex, args.chapter)
        if s:
            snippet = re.sub(r'\s+', ' ', row.get('text', '')).strip()[:500]
            hits.append({
                'score': s,
                'chunk_id': row.get('chunk_id'),
                'file': row.get('file'),
                'source_role': row.get('source_role'),
                'heading_path': row.get('heading_path'),
                'inferred_chapter': row.get('inferred_chapter'),
                'page_or_slide': row.get('page_or_slide'),
                'snippet': snippet,
            })
    hits.sort(key=lambda r: (-r['score'], r['file'] or '', r['chunk_id'] or ''))
    hits = hits[:args.limit]
    if args.json:
        print(json.dumps({'query': args.query, 'hits': hits}, ensure_ascii=False, indent=2))
        return
    print(f'# Search results for `{args.query}`\n')
    if not hits:
        print('No matches found.')
        return
    for i, hit in enumerate(hits, 1):
        heading = ' / '.join(hit.get('heading_path') or [])
        print(f"## {i}. {hit['file']} ({hit['source_role']}, score {hit['score']})")
        if heading:
            print(f"- heading: {heading}")
        if hit.get('page_or_slide'):
            print(f"- page/slide: {hit['page_or_slide']}")
        if hit.get('inferred_chapter'):
            print(f"- inferred chapter: {hit['inferred_chapter']}")
        print(f"\n{hit['snippet']}\n")

if __name__ == '__main__':
    main()
