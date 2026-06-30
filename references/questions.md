# Questions, coverage, and generated practice

## First-pass existing question extraction

When past papers, historical questions, homework questions, official review questions, question banks,课后习题, 复习题, 思考题, quizzes, assignments, or user-note question markers exist, extract them during the first scan before chapter writing.

Create `00_已有题目索引.md` as an inventory/routing file:

```markdown
# 已有题目索引

| 题目 | 来源文件 | 题目来源类型 | 章节 | 知识点 | 题型 | 是否有答案 | 是否已解析 | 后续处理 |
|---|---|---|---|---|---|---|---|---|
```

Use this index to:

- identify real exam weight and repeated topics;
- route questions to chapters;
- decide which notes need more depth;
- keep source questions separate from generated practice;
- drive coverage checks after chapter drafts are written.

Do not wait until the very end to discover that a chapter has many source questions.

## Historical/source questions

When source questions exist, process them after chapter notes are organized, but keep the first-pass question index available from the beginning.

First classify:

```markdown
# 历史题/来源题分析

| 题目 | 年份/来源 | 章节 | 知识点 | 题型 | 难度 | 是否已有笔记覆盖 |
|---|---|---|---|---|---|---|

## 高频考点

| 知识点 | 出现次数 | 涉及年份/来源 | 常见问法 | 对应笔记 |
|---|---:|---|---|---|
```

Then handle by answer state:

- Questions without answers: write answer + analysis + source + coverage status.
- Questions with answers but no analysis: preserve original answer, add analysis, verify against `teacher_ppt`, `textbook`, `official_handout`, `syllabus`, or `user_note` sources, and mark doubts.
- Questions with answers and analysis: organize, verify, source, extract question style, and check whether notes cover them.

Preserve original source answers. If a source answer is corrected, expanded, or reframed, separate the original answer from the organized answer and explain the basis. If a source answer conflicts with teacher PPT, textbook, official handout, syllabus, or user-note material, mark `来源冲突` and authority level rather than silently rewriting it.

Per-question format:

```markdown
### [来源/年份]-[题型]-[编号] 题目

## 题目
## 原始答案
## 整理后答案
## 解析
## 出处
## 依据级别
## 证据状态
## 当前笔记覆盖情况
## 是否需要补强
## 冲突/待核验
```

Use `原始答案` only when a source answer exists. Use `整理后答案` for the verified, study-ready answer. Keep corrections, assumptions, and uncertainty out of the original-answer section.

## Coverage classification

Use questions as a coverage audit, not only as practice.

| 类型 | 含义 | Required action |
|---|---|---|
| A：已明确整理 | Answer is clearly supported by existing chapter notes/concept cards. | Link the relevant note/source; no major rewrite needed. |
| B：笔记有覆盖，但答案更完整 | Notes contain the core point, but answer adds useful exam framing. | Fold the richer exam framing back into chapter notes or `05_典型考法.md`. |
| C：依赖外部补充，且已标记 | Answer uses external supplements already marked in notes/index. | Ensure the external source is marked and local-source authority is clear. |
| D：疑似先验/推断，需要加深 | Answer relies on inference or prior knowledge not clearly supported by current materials. | Resolve from local sources or log in `00_资料缺口与待确认.md`. |

Pair every A-D label with a provenance/support status when practical:

| Support status | Meaning |
|---|---|
| `directly_supported` / `明确依据` | A local source directly supports the answer or note claim. |
| `partially_supported` / `间接支持` | Local sources support the direction but not the full answer. |
| `contradicted` / `来源冲突` | Source answer, note, or material conflicts with another source. |
| `external_only` / `外部补充` | The answer depends on marked external material. |
| `inferred_pending_verification` / `待核验` | The answer still relies on inference and must not be presented as certain. |

Create or update `00_题目覆盖与笔记补强.md`:

```markdown
# 题目覆盖与笔记补强

| 题目 | 覆盖类型 | 证据状态 | 暴露问题 | 已补强到 | 仍需确认 |
|---|---|---|---|---|---|
```

When a draft note, source-question analysis, or generated practice file exists, use `scripts/coverage_check.py` against `.course_index/` as a conservative first pass, then review the result before writing B-D strengthening items.

For B-D items, apply strengthening when the source support is clear. If not clear, do not invent; log the gap and what should be checked. D items cannot be resolved by confident model inference alone: resolve from local sources, mark as `外部补充`, or keep as `待核验`.

## No-question fallback

If there are no official questions, historical questions, or review questions, do not stop. Build a self-check loop from notes:

1. Extract testable points from each chapter.
2. Generate chapter-level self-test questions that test course knowledge, not study strategy.
3. Generate answers, analysis, and source links.
4. Check whether current notes support the generated answers.
5. Strengthen notes if a question exposes a weak or missing explanation.

A valid generated question sounds like a teacher examining course content. Avoid meta-review prompts such as “为什么本章重要”, “为什么这一章是背景基础”, “你会怎么复习”, “如果考试让你解释你会从哪些方面作答”, or “这种复习策略有什么风险”. Those are planning/reflection prompts, not exam questions.

Good course-content question patterns:

- Define or explain a course concept using the course's own terminology.
- Compare two models, methods, objects, mechanisms, cases, systems, theories, authors, events, rules, or processes from the course.
- Describe a workflow, argument, timeline, rule-application chain, mechanism, or case path from input/source/condition to result/output/decision.
- Judge whether a technical, conceptual, historical, legal, theoretical, or applied statement is correct and explain why using course concepts.

Bad meta questions:

- 为什么说第一章主要是后面几章的背景基础，而不是公式推导重点？
- 如果考试让你解释某概念，你会从哪些方面作答？
- 第一章不太可能出大推导题，所以完全不用看，这种复习策略有什么风险？

## Final question bank

After source questions are processed or after the no-question fallback, generate a final practice bank. Separate source-derived questions from predicted/generated questions.

Recommended structure:

```markdown
# 模拟题库与答案解析

## A. 来源题整理
## B. 来源题变式
## C. 章节自测题
## D. 综合预测题
## E. 易错判断题
```

Each question should include:

| 字段 | 内容 |
|---|---|
| 题目 | ... |
| 题型 | 名词解释 / 简答 / 推导 / 计算 / 论述 / 判断 / 案例 / 规则适用 |
| 难度 | 低 / 中 / 高 |
| 考点 | ... |
| 答案 | ... |
| 解析 | ... |
| 出处 | `teacher_ppt` / `textbook` / `official_handout` / `syllabus` / `user_note` / `existing_vault` / `external_supplement` plus concrete source location when available |
| 依据级别 | 本地权威资料 / 课堂/用户笔记 / 来源题/历史题 / 既有笔记 / 外部补充 / 模型推断/待核验 |
| 证据状态 | 明确依据 / 间接支持 / 来源冲突 / 提取存疑 / 待核验 / 外部补充 |

Generated questions should cover both historical/source-question topics and important material that has not appeared in available questions. Every generated question must be directly answerable from course knowledge.

Generated practice must not retroactively create unsupported course facts. If an answer cannot be traced to local course content, marked external supplement, or explicit `待核验`, do not present it as certain.

## Final quality pass

| Check | Pass condition |
|---|---|
| Existing questions first | Source questions were indexed before generated practice. |
| Original answers preserved | Source-provided answers remain separate from organized/corrected answers. |
| Course-content question | The question tests a definition, concept, formula, model, comparison, process, timeline, theory, rule, case, application, applied reasoning, or judgment from the course. |
| Answerable | A student can write a direct answer without guessing the examiner's intent. |
| Source-backed | The answer can be linked to teacher PPT, textbook, official handout, syllabus, user notes, existing notes, or marked external supplement. |
| Provenance present | Answer/source fields include source role, source location when available, and evidence status. |
| Uncertainty preserved | Conflicts, extraction doubts, and unsupported inferences are marked rather than hidden. |
| External clearly marked | External supplements are labeled and subordinate to local materials. |
| Not meta | It is not about study strategy, chapter importance, or “how would you answer if asked”. |
| Coverage updated | B-D items are reflected in strengthened notes, `00_题目覆盖与笔记补强.md`, or gap files. |
