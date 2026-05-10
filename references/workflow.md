# Workflow and long-course execution

## Automatic workflow

When the user broadly asks to organize review materials, run this sequence:

1. Scan the provided folder/files.
2. Use lower-level document skills to extract PPT/PDF/DOCX content into text/Markdown when needed.
3. For folder or whole-course inputs, build or update `.course_index/` before chapter writing. Single short ad hoc tasks may work directly from visible text.
4. Classify source roles: teacher/textbook, user notes, historical/source questions, senior notes, existing vault, external supplements.
5. Extract existing questions from materials:课后习题, 复习题, 思考题, 历年题, 考试题, 作业题, 题库, quizzes, assignments, review questions, and user-note question markers.
6. Infer the chapter system from filenames, headings, tables of contents, slide titles, note headings, question groups, and repeated topics.
7. Classify the course knowledge type so the vault template fits the discipline.
8. Build a material inventory, existing-question inventory, chapter inference table, course-type judgment, and vault architecture plan.
9. Stop once at the initial architecture checkpoint. Ask only for corrections to chapter split, source roles, course type, or output architecture.
10. After approval or no objection, create all chapter tasks at once and process chapters in batches.
11. Report once per 6 chapters, not after every chapter.
12. After each batch, collect uncertainty, re-check local sources, and defer external research unless a gap blocks useful writing.
13. After all chapters, write whole-course relationship/review-route outputs.
14. Process source questions, run coverage checks, strengthen notes, and generate final practice questions.
15. Run a final external supplement pass only for unresolved local gaps when web/search is available and appropriate.

## Initial checkpoint wording

Use a concise checkpoint like:

> I found these materials, extracted these existing questions, inferred these chapters, classified this course as [course type], and plan this vault structure. Tell me now if the chapter split, source roles, course type, or output architecture are wrong; otherwise I will proceed through all chapters in batches and report every 6 chapters.

Do not add phase-by-phase permission questions.

## First-pass required artifacts

For folder or whole-course organization, create or plan these before chapter writing:

```text
.course_index/
├─ files.jsonl
├─ chunks.jsonl
├─ headings.jsonl
├─ questions.jsonl
├─ terms.jsonl
└─ progress.json
```

Inside the vault, create the global layer early and keep it updated:

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

- Build or update `.course_index/` before chapter writing.
- Use `chapter_pack.py` to gather only the current chapter context.
- Process chapters in blocks of 6 by default.
- At each report point, summarize paths changed, chapters completed, gaps found, source-question coverage, and the next automatic phase.
- When resuming, read `00_项目状态.md`, `00_章节进度表.md`, `00_题目覆盖与笔记补强.md`, and `.course_index/progress.json` first.
- If index files are missing or stale, rebuild them before continuing.

## Progress status vocabulary

Use stable statuses:

- `待整理`
- `整理中`
- `已整理`
- `需补强`
- `题目覆盖已检查`
- `外部补充已标记`
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
- Do not let external sources override teacher/textbook/user notes.
- Write external findings to `00_外部资料补充.md` or a chapter `外部资料标记` section.
- In exam-facing body text, mark external material lightly and keep local course wording authoritative.
