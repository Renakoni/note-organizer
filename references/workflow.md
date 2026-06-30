# Workflow and long-course execution

## Automatic workflow

When the user broadly asks to organize review materials, run this sequence:

1. Scan the provided folder/files.
2. Use lower-level document skills to extract PPT/PDF/DOCX content into text/Markdown when needed. For important PDFs with weak extraction, scanned pages, or encryption/unreadable errors, read `references/ingestion.md` and probe before relying on the result.
3. For folder or whole-course inputs, choose or create an output root that separates final notes, extracted text, index state, and temporary working files. Do not put OCR sidecars or chapter packs into the final note vault.
4. Check for an existing `.course_index/` first. If it is present and current, reuse it; otherwise build or update `.course_index/` from reliable extracted text or OCR sidecars before chapter writing. Single short ad hoc tasks may work directly from visible extracted text.
5. Classify source roles with the stable vocabulary: `teacher_ppt`, `textbook`, `official_handout`, `syllabus`, `user_note`, `source_question`, `historical_exam`, `assignment_or_quiz`, `senior_note`, `existing_vault`, `external_supplement`, or `unclassified_source`.
6. Extract existing questions from materials:课后习题, 复习题, 思考题, 历年题, 考试题, 作业题, 题库, quizzes, assignments, review questions, and user-note question markers.
7. Infer the chapter system from filenames, headings, tables of contents, slide titles, note headings, question groups, and repeated topics.
8. Classify the course knowledge type so the vault template fits the discipline.
9. Build a material inventory, existing-question inventory, chapter inference table, course-type judgment, and vault architecture plan.
10. Stop once at the initial architecture checkpoint. Ask only for corrections to chapter split, source roles, course type, or output architecture.
11. After approval or no objection, create all chapter tasks at once and process chapters in batches.
12. Report once per 6 chapters, not after every chapter.
13. After each batch, collect uncertainty, re-check local sources, and defer external research unless a gap blocks useful writing.
14. After all chapters, write whole-course relationship/review-route outputs.
15. Process source questions, run coverage checks, strengthen notes, and generate final practice questions.
16. Run a final external supplement pass only for unresolved local gaps when web/search is available and appropriate.
17. Run the final consistency check before claiming the note library is complete.

## Initial checkpoint wording

Use a concise checkpoint like:

> I found these materials, checked notable extraction-quality issues, extracted these existing questions, inferred these chapters, classified this course as [course type], and plan this vault structure. Tell me now if the chapter split, source roles, course type, or output architecture are wrong; otherwise I will proceed through all chapters in batches and report every 6 chapters.

Do not add phase-by-phase permission questions.

## Update and existing-vault workflow

When a `.course_index/` or an existing vault already exists, determine the user's real intent before doing broad work:

| User intent | Default behavior |
|---|---|
| Natural-language question about the course | Search existing `.course_index/` and vault `00_*.md` files first. Do not restart organization. |
| Continue a long job | Read saved progress and resume the next chapter, batch, coverage step, or final pass. |
| Revise one chapter | Build a chapter pack or search only impacted sources; preserve the rest of the vault. |
| Add new materials | Update the index once, classify the new source roles, then build an impact map. |
| Check question coverage | Use `questions.jsonl`, chapter notes, and `00_题目覆盖与笔记补强.md`; do not rewrite unrelated chapters. |
| Reorganize existing vault | Ask for confirmation only if folder architecture, chapter split, or source hierarchy will change. |

For existing vaults, read these before writing:

- `00_项目状态.md`
- `00_章节进度表.md`
- `00_资料索引.md`
- `00_资料缺口与待确认.md`
- `00_题目覆盖与笔记补强.md` when it exists
- `.course_index/progress.json` when it exists

When new or changed sources are present, create a compact impact map before editing:

| Change | Impact to check |
|---|---|
| New teacher PPT/textbook/official source | Source roles, chapter structure, definitions/formulas, existing uncertainty. |
| New source questions or past papers | `00_已有题目索引.md`, chapter routing, coverage table, final question bank. |
| New user notes | Emphasis markers, classroom priorities, personal weak points, `不确定内容`. |
| Changed extracted text | Affected chunks/headings/questions, extraction quality, already-written notes. |
| Newly OCRed or re-extracted PDF text | Source inventory, extraction-quality notes, affected chunks/questions, unresolved page gaps. |
| Deleted or missing source | Stale citations, broken source references, unresolved gap entries. |

Only stop for user confirmation during an update when one of these would change:

- chapter architecture;
- source-role classification for important materials;
- output structure;
- whether to overwrite or replace existing user-authored content.

Otherwise update impacted chapters/global files in batches and report what changed. If source authority is unclear, preserve existing notes and log the conflict instead of silently replacing content.

## First-pass required artifacts

For folder or whole-course organization, create or plan these before chapter writing:

```text
课程整理输出/
├─ 期末复习/                  # final Markdown/Obsidian vault
├─ _extracted/                # extracted PDF/PPT/DOCX text and OCR sidecars
├─ .course_index/             # machine-readable index/progress state
└─ _working/                  # temporary chapter packs and script scratch outputs
```

Inside the final vault, create the global layer early and keep it updated:

```text
期末复习/
├─ 00_总目录.md
├─ 00_项目状态.md
├─ 00_资料索引.md
├─ 00_章节进度表.md
├─ 00_术语索引.md
├─ 00_已有题目索引.md        # when source questions exist
├─ 00_题目覆盖与笔记补强.md
├─ 00_资料缺口与待确认.md
└─ 00_检索日志.md
```

`00_章节进度表.md` should track:

| 章节 | 状态 | 来源覆盖 | 题目覆盖 | 不确定点 | 下次动作 |
|---|---|---|---|---|---|

Use these files as the project memory for resume/continuation. Do not rely on chat history alone.

Prefer `.course_index/progress.json` for machine-readable state and the `00_*.md` files for user-readable decisions, gaps, and progress. The note library should remain usable from `.course_index/` and the vault files alone.

## Course knowledge-type classification

Classify the course before choosing chapter templates. The point is to avoid forcing model/formula structure onto subjects where the exam logic is theoretical, historical, legal, or case-based.

| Type | Use when | Third chapter file |
|---|---|---|
| 公式模型型 | formulas, models, derivations, algorithms, workflows dominate | `03_公式模型流程.md` |
| 概念理论型 | concepts, schools, theories, arguments, definitions dominate | `03_理论框架与论述逻辑.md` |
| 史实脉络型 | chronology, authors, events, periods, development paths dominate | `03_时间线与脉络.md` |
| 法条规范型 | rules, standards, legal provisions, applicability conditions dominate | `03_规则条文与适用条件.md` |
| 案例应用型 | cases, symptoms, mechanisms, interventions, applied scenarios dominate | `03_案例机制与处理流程.md` |
| 混合型 | different chapters have different knowledge forms | choose per chapter; document the choice in `00_项目状态.md` |

Keep file names concrete. Do not emit placeholders such as `03_某类型文件.md`.

## Batch/resume behavior

For long jobs:

- Check `.course_index/` before chapter writing. Reuse it when current; rebuild it when missing, stale, or tied to a different input directory.
- Use `chapter_pack.py` to gather only the current chapter context.
- Process chapters in blocks of 6 by default.
- At each report point, summarize paths changed, chapters completed, gaps found, source-question coverage, and the next automatic phase.
- When resuming, read `00_项目状态.md`, `00_章节进度表.md`, `00_题目覆盖与笔记补强.md`, and `.course_index/progress.json` first.
- If index files are missing or stale, rebuild them before continuing.

For resume decisions:

- If the user asks a natural-language question about an already organized course, search the existing index and vault first rather than restarting the automatic workflow.
- If the user asks to continue, use `progress.json` and `00_章节进度表.md` to identify the next chapter or coverage step.
- If new source files were added, update the index once, then continue from the saved progress.
- If the existing index contradicts the visible vault state, trust the user-readable vault files for decisions and rebuild the index before writing more chapters.

## Progress status vocabulary

Use stable statuses:

- `待整理`
- `整理中`
- `已整理`
- `待更新`
- `受新资料影响`
- `已更新`
- `需补强`
- `题目覆盖已检查`
- `外部补充已标记`
- `健康检查通过`
- `健康检查需复核`
- `存在来源冲突`
- `完成`

## Final external supplement pass

Use external research only after local material is insufficient. Prefer one bounded pass after local organization rather than scattered web lookups.

Trigger it when:

- `00_资料缺口与待确认.md` contains unresolved local gaps;
- B-D coverage items cannot be resolved from local materials;
- formula/model/background/context is too incomplete to make a useful study note;
- the user has allowed web/search use or the environment clearly supports it.

Rules:

- Search only the accumulated gaps, not the whole course generically.
- Prefer Tavily or the user's configured search tool when available.
- Do not let external sources override teacher PPT, textbook, official handout, syllabus, or user notes.
- Write external findings to `00_外部资料补充.md` or a chapter `外部资料标记` section.
- In exam-facing body text, mark external material lightly and keep local course wording authoritative.

## Final consistency check

Run this before claiming the course note library or update pass is complete. If a check is blocked or deferred, say so plainly and point to the relevant file.

Use `scripts/index_status.py` and `scripts/validate_vault.py` when the relevant paths are available; otherwise perform the same checks directly from the visible files.

| Check | Pass condition |
|---|---|
| Index/vault state | `.course_index/` is present and current enough for the task, or the final report explains why indexing was unnecessary or deferred. |
| Progress consistency | `.course_index/progress.json`, `00_项目状态.md`, and `00_章节进度表.md` agree on completed/pending chapters as far as they exist. |
| Material inventory | New or changed sources are reflected in `00_资料索引.md` with source role, update status, and extraction-quality notes when relevant. |
| Output separation | Final notes are in the vault; extracted/OCR text, `.course_index/`, and temporary packs are outside it. |
| Extraction quality | Important PDFs and image-heavy sources were either extracted reliably, OCRed into sidecars, or logged as unresolved with affected pages/files. |
| Source questions | Existing/source questions are indexed, routed, or explicitly marked absent; generated questions are separated from source questions. |
| Coverage | B-D coverage items were strengthened when source support was clear, or logged in `00_题目覆盖与笔记补强.md` / `00_资料缺口与待确认.md`. |
| Uncertainty | Contradictions, distorted extraction, missing answers, and unsupported inferences are visible in `不确定内容` or global gap files. |
| External supplements | External material is bounded to local gaps, marked in `00_外部资料补充.md` or chapter `外部资料标记`, and does not override local authority. |
| Preservation | Existing vault structure, human edits, source answers, and wikilinks were preserved unless explicitly changed or corrected by higher-authority local sources. |
| Final report | User-facing report lists completed updates, unresolved gaps, deferred checks, and the next automatic phase without overstating completion. |
