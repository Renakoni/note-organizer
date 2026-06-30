#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

TEXT_EXTS = {'.md', '.txt', '.markdown'}
GENERATED_DIRS = {'.course_index', '_working', '期末复习'}
CORE_FILES = [
    'files.jsonl',
    'chunks.jsonl',
    'headings.jsonl',
    'questions.jsonl',
    'terms.jsonl',
    'progress.json',
]


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
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def discover_sources(input_dir: Path, index_dir: Path):
    sources = []
    if not input_dir.exists():
        return sources
    for path in input_dir.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        rel_parts = path.relative_to(input_dir).parts
        if any(part in GENERATED_DIRS for part in rel_parts):
            continue
        try:
            path.relative_to(index_dir)
            continue
        except ValueError:
            pass
        sources.append(path)
    return sorted(sources)


def fingerprint(path: Path, input_dir: Path):
    stat = path.stat()
    return {
        'file': path.relative_to(input_dir).as_posix(),
        'size': stat.st_size,
        'mtime_ns': stat.st_mtime_ns,
    }


def pending_delta(current_rows, manifest_rows):
    old = {row.get('file'): row for row in manifest_rows if row.get('file')}
    current = {row.get('file'): row for row in current_rows if row.get('file')}
    added, changed, unchanged, deleted = [], [], [], []
    for rel, row in current.items():
        prev = old.get(rel)
        if not prev:
            added.append(rel)
        elif prev.get('size') == row.get('size') and prev.get('mtime_ns') == row.get('mtime_ns'):
            unchanged.append(rel)
        else:
            changed.append(rel)
    for rel in old:
        if rel not in current:
            deleted.append(rel)
    return {
        'added': sorted(added),
        'changed': sorted(changed),
        'unchanged': sorted(unchanged),
        'deleted': sorted(deleted),
    }


def count_rows(index_dir: Path):
    return {
        'files': len(read_jsonl(index_dir / 'files.jsonl')),
        'chunks': len(read_jsonl(index_dir / 'chunks.jsonl')),
        'headings': len(read_jsonl(index_dir / 'headings.jsonl')),
        'questions': len(read_jsonl(index_dir / 'questions.jsonl')),
        'terms': len(read_jsonl(index_dir / 'terms.jsonl')),
        'manifest': len(read_jsonl(index_dir / 'manifest.jsonl')),
    }


def quality_counts(index_dir: Path):
    counts = {}
    for row in read_jsonl(index_dir / 'files.jsonl'):
        key = row.get('extraction_quality') or 'uncertain'
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def build_status(index_dir: Path, input_dir_arg: str | None):
    progress = read_json(index_dir / 'progress.json', {}) or {}
    health = read_json(index_dir / 'health.json', {}) or {}
    input_dir = Path(input_dir_arg or progress.get('input_dir') or '').expanduser()
    row_counts = count_rows(index_dir)
    extraction_quality = quality_counts(index_dir)
    missing = [name for name in CORE_FILES if not (index_dir / name).exists()]
    warnings = list(health.get('warnings') or [])
    if missing:
        warnings.append('missing core index files: ' + ', '.join(missing))

    saved_counts = {
        'files': progress.get('files'),
        'chunks': progress.get('chunks'),
        'questions': progress.get('questions'),
        'terms': progress.get('terms'),
    }
    for key, saved in saved_counts.items():
        if saved is not None and row_counts.get(key) != saved:
            warnings.append(f'{key} count mismatch: progress={saved}, actual={row_counts.get(key)}')

    delta = {'added': [], 'changed': [], 'unchanged': [], 'deleted': []}
    if input_dir_arg or progress.get('input_dir'):
        if input_dir.exists():
            current = [fingerprint(path, input_dir) for path in discover_sources(input_dir, index_dir)]
            delta = pending_delta(current, read_jsonl(index_dir / 'manifest.jsonl'))
        else:
            warnings.append(f'input directory not found: {input_dir}')

    if delta['added'] or delta['changed'] or delta['deleted']:
        warnings.append('source changes pending: added={added}, changed={changed}, deleted={deleted}'.format(
            added=len(delta['added']),
            changed=len(delta['changed']),
            deleted=len(delta['deleted']),
        ))

    status = 'ok' if not warnings else 'needs_review'
    return {
        'status': status,
        'index_dir': str(index_dir),
        'input_dir': str(input_dir) if str(input_dir) != '.' else '',
        'version': progress.get('version'),
        'last_indexed_at': progress.get('indexed_at'),
        'health_status': health.get('status'),
        'saved_counts': saved_counts,
        'actual_counts': row_counts,
        'extraction_quality': extraction_quality,
        'pending_delta': {key: len(value) for key, value in delta.items()},
        'pending_files': {key: value[:20] for key, value in delta.items() if key != 'unchanged' and value},
        'warnings': warnings,
    }


def print_markdown(status):
    print('# Index status\n')
    print(f"- Status: {status['status']}")
    print(f"- Index: {status['index_dir']}")
    if status.get('input_dir'):
        print(f"- Input: {status['input_dir']}")
    if status.get('version'):
        print(f"- Version: {status['version']}")
    if status.get('last_indexed_at'):
        print(f"- Last indexed: {status['last_indexed_at']}")
    counts = status['actual_counts']
    print(f"- Counts: files={counts['files']}, chunks={counts['chunks']}, questions={counts['questions']}, terms={counts['terms']}")
    if status.get('extraction_quality'):
        print('- Extraction quality: ' + ', '.join(f"{k}={v}" for k, v in status['extraction_quality'].items()))
    delta = status['pending_delta']
    print(f"- Pending source delta: added={delta['added']}, changed={delta['changed']}, deleted={delta['deleted']}")
    if status['warnings']:
        print('\n## Warnings')
        for warning in status['warnings']:
            print(f"- {warning}")
    else:
        print('\nNo warnings.')


def main():
    ap = argparse.ArgumentParser(description='Report lightweight course index status without rewriting it.')
    ap.add_argument('index_dir')
    ap.add_argument('--input-dir', default='', help='Source folder to compare against manifest.jsonl.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    status = build_status(Path(args.index_dir), args.input_dir or None)
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_markdown(status)


if __name__ == '__main__':
    main()
