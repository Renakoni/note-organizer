# Material ingestion and extraction quality

Use this reference when materials include PDFs, scanned documents, image-heavy slides, screenshots, OCR output, or when a document skill reports that a file is encrypted, unreadable, empty, or malformed.

## Intake order

For folder or whole-course jobs, do not move straight from raw files to chapter writing. First establish whether the material has readable text:

1. Inventory source files and preserve their original paths.
2. Probe PDFs before trusting a single extraction failure.
3. Extract normal PDF/PPTX/DOCX files with the lower-level document skills.
4. For scanned or image-only PDFs, create OCR text sidecars in the output root's `_extracted/` folder when OCR tools are available.
5. Index extracted Markdown/text sidecars with `.course_index/`.
6. Record extraction quality in `00_资料索引.md`, `00_资料缺口与待确认.md`, and chapter `不确定内容` sections when relevant.

## PDF probe

Use `scripts/pdf_probe.py` before accepting claims such as "encrypted", "empty", or "no text" for important PDFs:

```bash
python scripts/pdf_probe.py MATERIAL_DIR
python scripts/pdf_probe.py MATERIAL_DIR --json
python scripts/pdf_probe.py path/to/file.pdf --pages 20
```

Treat the result as diagnostic evidence:

| Probe result | Default action |
|---|---|
| `text_extract` | Extract text/Markdown normally, then index the extracted output. |
| `mixed_extract_then_ocr_low_text_pages` | Extract available text, OCR low-text pages or the whole PDF if page-level OCR is unavailable, and mark remaining weak pages. |
| `ocr_sidecar` | Run OCR when available; otherwise log the source as unreadable enough for review. |
| `lower_level_retry` | Try another extractor before declaring the file unreadable. |
| `password_required_or_corrupt` | Ask for a password only if independent probes agree that text cannot be opened without one; otherwise mark the parser failure and try another extraction path. |

## False encrypted PDF reports

Do not tell the user a PDF is encrypted based on one failed parser or one lower-level skill error. PDF tools can disagree because:

- a PDF can have an owner password or permission flags while still opening with an empty user password;
- a parser may label a security handler as encrypted even when text extraction is allowed;
- malformed cross-reference tables, incremental updates, object streams, damaged metadata, or unsupported filters can surface as misleading encryption errors;
- some extractors fail on a page or embedded object and report the whole file as protected.

Before treating a PDF as truly password-blocked:

1. Run `pdf_probe.py` and inspect both PyMuPDF and pypdf status when available.
2. If either tool extracts meaningful text, treat the PDF as readable and log the other tool's failure as parser-specific.
3. If text is empty but pages and images exist, treat it as scanned/image-only unless a probe clearly says a password is required.
4. Ask for a password only when probes consistently show the document needs one and no text can be extracted.

## OCR sidecars

Keep OCR output as a separate extracted source rather than overwriting the original PDF or mixing it into the final vault. Prefer the output root's `_extracted/` folder:

```text
_extracted/
├─ lecture01.pdf.md
├─ textbook.ocr.txt
└─ past_exam.ocr.md
```

Then build `.course_index/` from `_extracted/` or another source-only material folder, not from the final vault.

When OCRmyPDF is installed, a useful pattern is:

```bash
ocrmypdf -l chi_sim+eng --rotate-pages --deskew --sidecar textbook.ocr.txt textbook.pdf textbook.ocr.pdf
```

Use languages that match the material, such as `chi_sim+eng` for simplified Chinese plus English. If OCR tools are missing, do not invent text. Log the file and affected pages as `提取存疑` or `待核验`.

## Images, formulas, and diagrams

OCR is not enough for visual meaning. For screenshots, formula-heavy pages, charts, diagrams, tables, handwritten boards, and slide screenshots:

- use OCR for visible text;
- use visual inspection or a vision-capable model only for concise descriptions of the figure, chart, layout, or formula;
- mark model-derived visual interpretation as `提取存疑` or `待核验` unless the same fact is supported by readable local text;
- keep page/slide references in the note or gap file;
- do not let OCR fragments become confident definitions, formulas, or exam answers without source confirmation.

## Extraction quality labels

Use these labels consistently in index rows, material inventories, gap files, and source audit sections:

| Label | Use when |
|---|---|
| `good` | Text is readable and complete enough for normal chapter writing. |
| `partial` | Some text is readable, but important pages, tables, formulas, or sections may be missing. |
| `poor` | Text is very short, broken, garbled, or too sparse for confident synthesis. |
| `empty` | No usable extracted text exists. |
| `image_only` | Pages appear to be scanned images or screenshots with little/no text layer. |
| `uncertain` | Tools disagree, file structure is unusual, or extraction quality cannot be judged from the current evidence. |

## Notes and reports

When extraction is weak, keep user-facing reports short and concrete:

- say which files/pages are affected;
- say what was attempted;
- say whether OCR sidecars were created or missing;
- write durable gaps to `00_资料缺口与待确认.md`;
- avoid claiming that a chapter, formula, table, or source question is fully covered when the supporting pages were not reliably extracted.
