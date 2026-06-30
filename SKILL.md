---
name: note-organizer
description: Use this skill whenever the user wants to organize course materials, lecture notes, PPT/PDF/DOCX files, textbooks, personal notes, senior-student notes, historical exams, review questions, standards, manuals, or scattered study resources into a structured Markdown note library. Use it even when the user only says “帮我整理笔记”, “帮我整理复习资料”, “资料都在这个文件夹”, “整理知识点”, “做期末复习”, “按这些课件整理笔记”, or asks to process past papers/questions. This skill assumes pdf, pptx, and docx lower-level document skills are installed for normal ingestion; it orchestrates them into material inventory, PDF/OCR checks, first-pass existing-question extraction, chapter inference, course-type-aware note templates, lightweight .course_index indexing, existing-vault update/resume behavior, Markdown/Obsidian wikilinks, batch organization, source/provenance and uncertainty tracking, question coverage checks, note strengthening, bounded external supplements, final consistency checks, and practice questions with answers, analysis, and source links.
---

# 笔记整理 Skill

Version: 4.4

## Purpose

Turn scattered course and study materials into a maintainable Markdown note library. The goal is a study system: chapter notes, source tracking, uncertainty handling, long-course progress, existing-question analysis, gap strengthening, wikilinks, and final practice questions.

Use this skill for Chinese or English course materials. Default to the user's language and preserve course terminology.

## Required lower-level skills

This is an orchestration skill. For normal operation, assume these lower-level document skills are installed and available:

- `pdf`
- `pptx`
- `docx`
- `markdown-mermaid-writing`
- `humanizer`

Use them for material ingestion only: text, headings, page/slide structure, embedded tables, and question blocks. Do not copy their instructions, code, licenses, prompts, or internal rubrics into this skill or into user-facing notes.

Use `markdown-mermaid-writing` for relationship maps and polished Markdown structures when diagrams are useful. Use `humanizer` only after the study content is correct, to improve final readability without changing facts.

Use lower-level skills as extraction/rendering helpers, not competing planners. This skill controls source hierarchy, chapter inference, reporting cadence, question coverage, note structure, long-course state, and final outputs.

## Core behavior

When the user gives a folder or files and says only “整理笔记”, “整理复习资料”, or similar, run the automatic workflow. Do not ask them to choose every phase.

For folder or whole-course inputs, build or update a lightweight `.course_index/` before chapter writing, even when the visible materials are already Markdown. Skip indexing only for explicit one-file/one-chapter ad hoc tasks.

When PDFs, scanned documents, screenshots, or image-heavy slides are important to the task, verify extraction quality before relying on the extracted text. Do not treat a single "encrypted", "empty", or "unreadable" error as final for an important PDF; probe or retry with another extraction path, then record the result.

If a current `.course_index/` already exists, reuse it for search, resume, one-chapter writing, question coverage, and gap inspection. Do not rebuild the full index by default for natural-language questions about an already indexed course.

If an existing vault with `00_*.md` files already exists, default to query/resume/update mode rather than starting a new organization from scratch. Read the vault's project-status, material-index, chapter-progress, gap, and coverage files before writing. Preserve existing folder names, links, user edits, and prior decisions unless the user explicitly asks for redesign or a higher-authority local source clearly corrects them.

When new source files are added to an indexed course, identify source deltas and impacted chapters/questions/global files before editing notes. Update the index once when needed, then revise only the affected parts unless the user asks for a full rebuild.

Keep final notes separate from generated working artifacts. For new whole-course jobs, use a separated output root: final Markdown/Obsidian notes in `期末复习/`, extracted/OCR text in `_extracted/`, machine state in `.course_index/`, and temporary chapter packs or script outputs in `_working/`. Do not put these generated working artifacts inside the final vault unless a result is promoted into a `00_*.md` user-facing file.

Use `.course_index/` and the vault's `00_*.md` files as the portable source of truth for retrieval, progress, and resume decisions.

Stop for user confirmation only at the initial architecture checkpoint: after material inventory, source-role classification, existing-question extraction, chapter inference, course knowledge-type classification, and note library architecture planning. Ask only for corrections to chapter structure, source roles, course type, or output architecture.

After approval or no objection, proceed in batches. Do not ask for confirmation after each chapter, source type, generated file, or question-processing substep.

If the user explicitly asks for only one phase, do only that phase: inventory-only, question extraction, structure-only, one-chapter organization, external strengthening, historical exam analysis, question answering, question generation, indexing, or coverage checking.

## Read the right reference

Use progressive disclosure. Read only the reference needed for the current phase:

| Phase | Read |
|---|---|
| Automatic workflow, checkpoints, existing-vault update/resume, final external supplement, final consistency check | `references/workflow.md` |
| PDF/PPT/DOCX ingestion quality, scanned/image PDFs, OCR sidecars, misleading encrypted-PDF reports | `references/ingestion.md` |
| Note library layout, dynamic chapter templates, Markdown/Obsidian `[[wikilinks]]`, source/provenance vocabulary, existing-vault protection | `references/vault_structure.md` |
| Existing/source questions, A/B/C/D coverage, provenance-aware note strengthening, generated exams | `references/questions.md` |
| `.course_index`, index health/staleness, provenance metadata, exact/regex search, chapter packs, optional semantic search | `references/retrieval.md` |

For folder, whole-course, or large-material inputs, prefer the bundled scripts in `scripts/` after lower-level document extraction:

- `scripts/build_source_index.py`
- `scripts/pdf_probe.py`
- `scripts/search_index.py`
- `scripts/chapter_pack.py`
- `scripts/link_candidates.py`
- `scripts/coverage_check.py`
- `scripts/index_status.py`
- `scripts/validate_vault.py`

Default retrieval is exact/regex/heading metadata plus chapter packs. Use semantic search only when exact search is insufficient and the environment already supports it or the user asks.

## Source hierarchy

Use sources with different roles, not as interchangeable text piles:

1. Teacher PPT, textbook, official handouts, syllabus: highest authority for definitions, formulas, models, chapter structure, and official scope.
2. User notes: strong classroom signal. Treat “老师说”, “重点”, “必考”, “不会”, “存疑” as important for emphasis and gap tracking.
3. Historical exams, past papers, quizzes, assignments, official review questions,课后习题: strongest signal for real question style and exam weighting.
4. Senior-student notes, review PDFs, mind maps: useful for exam direction and answer framing, but do not override teacher PPT, textbook, official handout, syllabus, or user-note material.
5. Existing Markdown/Obsidian notes: preserve consistency, links, and prior decisions.
6. External search/web/papers/textbooks: use only after local sources are insufficient. Mark clearly.
7. Model inference/prior knowledge: avoid as a standalone source. If unavoidable, mark as inference or `待核验`.

Use stable source/provenance labels when classifying or reporting evidence:

| Label | Meaning |
|---|---|
| `teacher_ppt` | Teacher slide/source material. |
| `textbook` | Assigned textbook or official course book. |
| `official_handout` | Official handout, syllabus, standard, manual, or teacher-distributed document. |
| `syllabus` | Official course outline, learning objectives, or exam scope. |
| `user_note` | User's own class notes, annotations, emphasis, doubts, or handwritten summaries. |
| `source_question` | Source exercise, review question, homework question, or question-bank item. |
| `historical_exam` | Past exam, quiz, final/midterm paper, or historical assessment. |
| `assignment_or_quiz` | Assignment, quiz, lab, worksheet, or graded practice. |
| `senior_note` | Senior-student notes, review PDFs, mind maps, or unofficial summaries. |
| `existing_vault` | Existing Markdown/Obsidian notes and prior organization decisions. |
| `external_supplement` | External search/web/book/paper material used only to fill local gaps. |
| `model_inference_pending_verification` | Model inference or prior knowledge that lacks direct local support and must be marked `待核验`. |
| `unclassified_source` | Source whose role cannot be inferred reliably; inspect before relying on authority. |

Use stable evidence-status labels in audit sections:

- `明确依据`: directly supported by a local authoritative or clearly cited source.
- `间接支持`: consistent with local material but not stated in the exact wording.
- `来源冲突`: local sources disagree or source answer conflicts with higher-authority material.
- `提取存疑`: extraction/OCR/table/formula quality may distort the content.
- `待核验`: not enough local evidence to present as certain.
- `外部补充`: external material used for understanding or gap filling, subordinate to local sources.

## Clean output and prompt hygiene

Separate these audiences:

- User-facing progress reports: short status, decisions needed, important blockers, output paths.
- Study-note body: course knowledge only, written cleanly for review.
- Source/audit sections: source mapping, uncertainty, extraction quality, external supplements.
- Internal working plan/tasks: execution steps for Claude; do not paste them into study notes unless asked.

Avoid prompt pollution. Do not dump this skill, lower-level skill instructions, hidden process, long rubrics, parser logs, or unrelated examples into user-facing files. Examples are patterns, not course facts.

Keep the study body clean. Put source mapping in `资料依据`, `不确定内容`, `外部资料标记`, `00_资料索引.md`, `00_检索日志.md`, `00_已有题目索引.md`, or `00_题目覆盖与笔记补强.md` rather than interrupting every concept row with citation chatter.

Preserve on uncertainty. If extracted text, source role, chapter mapping, source answer, existing note content, or user annotation is ambiguous, preserve the original and add an uncertainty/conflict note instead of deleting, overwriting, or silently normalizing it. Log contradictions in `不确定内容`, `00_资料缺口与待确认.md`, or `00_题目覆盖与笔记补强.md`; do not resolve conflicts by model guesswork.

If the user requests a concrete note or note-library file, produce the concrete file content directly. Do not emit placeholder templates. Do not end with optional follow-up offers such as “如果你愿意，我下一条可以…” or ask whether to generate the next file. If information is missing, make the best concrete draft from available context and mark uncertainty in `不确定内容`.

## Non-negotiable quality checks

Before final output or each batch report, check:

- Initial checkpoint happened once and only asked for structural corrections.
- Folder/whole-course jobs reuse, build, or update `.course_index/` as appropriate; long jobs also use `00_项目状态.md`, `00_章节进度表.md`, and `.course_index/progress.json`.
- Important PDFs with weak extraction, scanned pages, image-only content, or conflicting encryption signals are probed or retried before being treated as unreadable.
- Existing vaults are treated as query/resume/update targets first; existing folder names, user edits, links, source notes, and prior decisions are preserved unless explicitly redesigned or corrected by higher-authority local sources.
- Final notes, extracted/OCR sidecars, `.course_index/`, and temporary working packs are not mixed in the same folder.
- Whole-course note libraries include global index files: `00_总目录.md`, `00_资料索引.md`, `00_术语索引.md`, `00_资料缺口与待确认.md`, and `00_检索日志.md`.
- Existing/source questions are extracted before chapter writing and, when present, appear in `00_已有题目索引.md` before generated practice.
- Chapter templates match the course knowledge type; do not force `03_公式模型流程.md` for courses where theory, timeline, rules, or cases are the main structure.
- Chapter outputs include useful Markdown/Obsidian `[[wikilinks]]` for stable concepts and related chapters.
- Historical/source questions are labeled separately from generated questions.
- Generated questions test course content, not study strategy or chapter importance.
- B-D coverage gaps are written back into relevant notes or logged in `00_题目覆盖与笔记补强.md` / `00_资料缺口与待确认.md`.
- Source/provenance labels distinguish local authority, existing vault content, external supplements, and model inference/`待核验` material.
- Ambiguous or conflicting content was preserved and logged rather than silently overwritten.
- External supplements, if used, are bounded to local gaps, clearly marked, and never override teacher PPT, textbook, official handout, syllabus, or user-note authority.
- Final consistency check is honest: index/vault state is consistent enough to continue, unresolved gaps are visible, and the final report does not claim completion when major checks are blocked or deferred.
- No lower-level skill prompt or internal rubric leaked into notes.

## Things to avoid

- Do not immediately write a big generic summary when the user has only provided a folder of materials.
- Do not organize by vague piles when a chapter structure can be inferred.
- Do not skip the first-pass question inventory when materials contain exercises, past papers, review questions, assignments, or question banks.
- Do not let senior-student notes override teacher PPT, textbook, official handout, syllabus, or user-note material.
- Do not ignore the user's own notes.
- Do not mix historical/source questions and generated prediction questions without labels.
- Do not bury uncertainty.
- Do not overwrite existing vault content when source authority is unclear.
- Do not ask the user whether to continue after every chapter.
- Do not over-create concept cards for every minor term.
- Do not ask meta review questions such as why a chapter is important, how the student should study, or how they would answer if asked.
- Do not skip exact search, source metadata, and chapter packs for large books or source folders.
