#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

LOW_TEXT_CHARS = 40
GOOD_TEXT_CHARS = 300


def import_module(name):
    try:
        return __import__(name)
    except Exception as exc:
        return exc


def discover_pdfs(paths):
    pdfs = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            pdfs.extend(sorted(p for p in path.rglob('*.pdf') if p.is_file()))
        elif path.is_file() and path.suffix.lower() == '.pdf':
            pdfs.append(path)
    seen = set()
    out = []
    for path in pdfs:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            out.append(path)
    return out


def probe_with_pymupdf(path: Path, page_limit: int | None):
    fitz = import_module('fitz')
    if isinstance(fitz, Exception):
        return {'available': False, 'error': f'{type(fitz).__name__}: {fitz}'}

    result = {'available': True}
    try:
        doc = fitz.open(path)
        result['is_encrypted'] = bool(getattr(doc, 'is_encrypted', False))
        result['needs_password'] = bool(getattr(doc, 'needs_pass', False))
        result['empty_password_ok'] = None
        if result['needs_password']:
            try:
                result['empty_password_ok'] = bool(doc.authenticate(''))
            except Exception:
                result['empty_password_ok'] = False
        if result['needs_password'] and not result['empty_password_ok']:
            result['pages'] = getattr(doc, 'page_count', 0)
            result['error'] = 'password required'
            doc.close()
            return result

        pages = int(getattr(doc, 'page_count', 0))
        limit = min(pages, page_limit) if page_limit else pages
        page_rows = []
        for index in range(limit):
            page = doc.load_page(index)
            try:
                text = page.get_text('text') or ''
            except Exception:
                text = ''
            try:
                image_count = len(page.get_images(full=True))
            except Exception:
                image_count = None
            chars = len(text.strip())
            page_rows.append({
                'page': index + 1,
                'chars': chars,
                'low_text': chars < LOW_TEXT_CHARS,
                'images': image_count,
            })
        doc.close()
        result['pages'] = pages
        result['sampled_pages'] = limit
        result['page_text'] = page_rows
        return result
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
        return result


def probe_with_pypdf(path: Path, page_limit: int | None):
    pypdf = import_module('pypdf')
    if isinstance(pypdf, Exception):
        return {'available': False, 'error': f'{type(pypdf).__name__}: {pypdf}'}

    result = {'available': True}
    try:
        reader = pypdf.PdfReader(str(path), strict=False)
        result['is_encrypted'] = bool(getattr(reader, 'is_encrypted', False))
        result['empty_password_ok'] = None
        if result['is_encrypted']:
            try:
                decrypt_result = reader.decrypt('')
                result['empty_password_ok'] = bool(decrypt_result)
            except Exception:
                result['empty_password_ok'] = False
        if result['is_encrypted'] and not result['empty_password_ok']:
            try:
                result['pages'] = len(reader.pages)
            except Exception:
                result['pages'] = 0
            result['error'] = 'password required'
            return result

        pages = len(reader.pages)
        limit = min(pages, page_limit) if page_limit else pages
        page_rows = []
        for index in range(limit):
            try:
                text = reader.pages[index].extract_text() or ''
            except Exception:
                text = ''
            chars = len(text.strip())
            page_rows.append({
                'page': index + 1,
                'chars': chars,
                'low_text': chars < LOW_TEXT_CHARS,
            })
        result['pages'] = pages
        result['sampled_pages'] = limit
        result['page_text'] = page_rows
        return result
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
        return result


def summarize_text(pages):
    sampled = len(pages)
    chars = [row.get('chars', 0) for row in pages]
    total_chars = sum(chars)
    low_pages = sum(1 for n in chars if n < LOW_TEXT_CHARS)
    good_pages = sum(1 for n in chars if n >= GOOD_TEXT_CHARS)
    return {
        'sampled_pages': sampled,
        'total_chars': total_chars,
        'avg_chars_per_sampled_page': round(total_chars / sampled, 1) if sampled else 0,
        'low_text_pages': low_pages,
        'good_text_pages': good_pages,
        'low_text_ratio': round(low_pages / sampled, 3) if sampled else 0,
    }


def classify(path: Path, pymupdf_result, pypdf_result):
    candidates = []
    for engine, result in [('pymupdf', pymupdf_result), ('pypdf', pypdf_result)]:
        pages = result.get('page_text') or []
        if pages:
            summary = summarize_text(pages)
            candidates.append((engine, result, summary))

    readable = [item for item in candidates if item[2]['total_chars'] > 0]
    best = max(readable, key=lambda item: item[2]['total_chars'], default=None)
    pages_total = max([r.get('pages') or 0 for r in (pymupdf_result, pypdf_result)] or [0])

    password_signals = [
        r for r in (pymupdf_result, pypdf_result)
        if r.get('error') == 'password required'
    ]
    extracted_despite_encryption = bool(best) and any(
        r.get('is_encrypted') for r in (pymupdf_result, pypdf_result)
    )

    if best:
        summary = best[2]
        low_ratio = summary['low_text_ratio']
        if low_ratio >= 0.85:
            quality = 'image_only'
            action = 'ocr_sidecar'
        elif low_ratio >= 0.2:
            quality = 'partial'
            action = 'mixed_extract_then_ocr_low_text_pages'
        elif summary['avg_chars_per_sampled_page'] >= GOOD_TEXT_CHARS:
            quality = 'good'
            action = 'text_extract'
        else:
            quality = 'partial'
            action = 'text_extract'
        return {
            'pages': pages_total,
            'best_text_engine': best[0],
            'text_summary': summary,
            'extraction_quality': quality,
            'recommended_action': action,
            'encrypted_but_readable': extracted_despite_encryption,
        }

    if password_signals and len(password_signals) == sum(1 for r in (pymupdf_result, pypdf_result) if r.get('available')):
        quality = 'uncertain'
        action = 'password_required_or_corrupt'
    elif pages_total > 0:
        quality = 'image_only'
        action = 'ocr_sidecar'
    else:
        quality = 'uncertain'
        action = 'lower_level_retry'
    return {
        'pages': pages_total,
        'best_text_engine': None,
        'text_summary': summarize_text([]),
        'extraction_quality': quality,
        'recommended_action': action,
        'encrypted_but_readable': False,
    }


def probe_pdf(path: Path, page_limit: int | None):
    pymupdf_result = probe_with_pymupdf(path, page_limit)
    pypdf_result = probe_with_pypdf(path, page_limit)
    summary = classify(path, pymupdf_result, pypdf_result)
    return {
        'file': str(path),
        **summary,
        'engines': {
            'pymupdf': pymupdf_result,
            'pypdf': pypdf_result,
        },
    }


def print_markdown(results):
    print('# PDF extraction probe\n')
    for row in results:
        text = row.get('text_summary') or {}
        print(f"## {row['file']}")
        print(f"- Pages: {row.get('pages', 0)}")
        print(f"- Best text engine: {row.get('best_text_engine') or 'none'}")
        print(f"- Extraction quality: {row.get('extraction_quality')}")
        print(f"- Recommended action: {row.get('recommended_action')}")
        print(
            '- Text sample: '
            f"sampled_pages={text.get('sampled_pages', 0)}, "
            f"total_chars={text.get('total_chars', 0)}, "
            f"avg_chars={text.get('avg_chars_per_sampled_page', 0)}, "
            f"low_text_pages={text.get('low_text_pages', 0)}"
        )
        if row.get('encrypted_but_readable'):
            print('- Note: at least one engine reported encryption, but text was still extractable.')
        for name, engine in row.get('engines', {}).items():
            if not engine.get('available'):
                print(f"- {name}: unavailable ({engine.get('error')})")
            elif engine.get('error'):
                print(f"- {name}: {engine.get('error')}")
            else:
                flags = []
                if engine.get('is_encrypted'):
                    flags.append('encrypted flag')
                if engine.get('needs_password'):
                    flags.append('needs password')
                if engine.get('empty_password_ok') is True:
                    flags.append('empty password ok')
                print(f"- {name}: ok" + (f" ({', '.join(flags)})" if flags else ''))
        print()


def main():
    parser = argparse.ArgumentParser(description='Probe PDF text layers, encryption signals, and OCR need.')
    parser.add_argument('paths', nargs='+', help='PDF files or folders to scan.')
    parser.add_argument('--pages', type=int, default=0, help='Limit sampled pages per PDF. Default scans all pages.')
    parser.add_argument('--json', action='store_true', help='Print JSON instead of Markdown.')
    args = parser.parse_args()

    page_limit = args.pages if args.pages and args.pages > 0 else None
    pdfs = discover_pdfs(args.paths)
    results = [probe_pdf(path, page_limit) for path in pdfs]
    if args.json:
        print(json.dumps({'pdfs': results}, ensure_ascii=False, indent=2))
    else:
        if not results:
            print('# PDF extraction probe\n\nNo PDF files found.')
        else:
            print_markdown(results)


if __name__ == '__main__':
    main()
