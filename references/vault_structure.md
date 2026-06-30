# Vault structure and Obsidian links

## Default vault architecture

If no suitable structure exists, create a separated output root. Keep generated working artifacts outside the final vault:

```text
课程整理输出/
├─ 期末复习/                  # final Markdown/Obsidian vault
├─ _extracted/                # extracted text, OCR sidecars, converted Markdown
├─ .course_index/             # index/progress JSONL files
└─ _working/                  # temporary chapter packs and script scratch files
```

Do not move the user's original source files unless asked. If an existing output layout already separates notes and working artifacts, follow it.

Inside the final vault, use a chapter-based structure:

```text
期末复习/
├─ 00_总目录.md
├─ 00_项目状态.md
├─ 00_资料索引.md
├─ 00_章节进度表.md
├─ 00_术语索引.md
├─ 00_已有题目索引.md            # if source/existing questions exist
├─ 00_题目覆盖与笔记补强.md
├─ 00_资料缺口与待确认.md
├─ 00_检索日志.md
├─ 00_外部资料补充.md            # if external supplements are used
├─ 00_全书知识关系与复习路线.md
├─ 00_考前速记与最后冲刺.md
├─ 00_历史题分析.md              # if historical/past questions exist
├─ 00_来源题逐题解析.md          # if source questions exist
├─ 00_自建题库.md                # if no questions exist, or final practice bank
├─ 01_第一章_xxx/
│  ├─ 01_章节总览.md
│  ├─ 02_核心概念.md
│  ├─ 03_公式模型流程.md          # or a course-type-specific file name
│  ├─ 04_易混淆点.md
│  ├─ 05_典型考法.md
│  ├─ 06_自测题.md
│  └─ 概念卡片/
└─ ...
```

If a vault or skeleton already exists, read it first and follow existing folder/file names. Do not redesign, rename, or create competing main directories unless the user asks.

During updates, preserve existing headings, links, source notes, user annotations, original answers, and prior architecture decisions. Add new content as clearly marked additions or targeted revisions. Do not restructure for aesthetics. Replace existing content only when the user requests it or a higher-authority local source clearly corrects it; otherwise keep the original and add a `不确定内容` entry.

## Dynamic chapter templates

Choose the chapter's third file from the course knowledge type. The aim is to match the way the subject is examined, not to force every subject into formulas.

| Course type | Third file | Include |
|---|---|---|
| 公式模型型 | `03_公式模型流程.md` | formulas, models, parameter meanings, assumptions, solved workflows, Mermaid processes |
| 概念理论型 | `03_理论框架与论述逻辑.md` | theories, schools, claims, argument structures, answer skeletons for essay questions |
| 史实脉络型 | `03_时间线与脉络.md` | timelines, periods, figures, events, cause-effect chains, comparison axes |
| 法条规范型 | `03_规则条文与适用条件.md` | rules, provisions, standards, applicability conditions, exceptions, case application |
| 案例应用型 | `03_案例机制与处理流程.md` | cases, mechanisms, diagnostic/decision logic, practical workflows, scenario handling |
| 混合型 | choose per chapter | record the selected template logic in `00_项目状态.md` |

Keep the rest of the chapter structure stable unless an existing vault already defines a different pattern.

## Obsidian wikilink rules

Use `[[双链]]` for stable reusable concepts, chapter pages, whole-course files, and cross-chapter dependencies. The goal is navigability, not decoration.

Minimum expectations:

- Each chapter overview links to `[[00_全书知识关系与复习路线]]`.
- Each chapter overview links to adjacent or dependent chapters, for example `[[02_第二章_坐标系统与几何模型]]`.
- Global index files link to chapter pages and stable concept cards when useful.
- First important mention of recurring concepts uses consistent links, for example `[[RPC模型]]`, `[[DEM]]`, `[[中心投影成像]]`.
- For indexed materials, run `link_candidates.py` for the current chapter and prefer real source terms from `teacher_ppt`, `textbook`, `official_handout`, `syllabus`, `user_note`, and question hits over generic links such as `[[基本概念]]`. Treat script output as candidates: use high-quality concept/object/formula/model/process terms, and skip status markers or sentence-like phrases such as `[[存疑]]`, `[[不会]]`, or `[[某原则包括...]]`.
- Do not link every ordinary word.

When the user asks for a concrete output, do not use placeholders such as `<章节名>`, `核心概念A`, `第二章_章节名`, or `前置章节_章节名`. If the exact material is unavailable in a dry run, use a realistic generic-but-valid concrete name such as `[[第一章_绪论]]`, `[[第二章_核心模型]]`, `[[核心概念]]`, and mark uncertainty in `不确定内容` rather than emitting placeholder tokens. Do not end a completed note with an optional follow-up offer; the note should end at the note content.

Before finalizing vault files, run a link quality pass. When the vault exists on disk, prefer `scripts/validate_vault.py` for a first pass, then review any warnings before claiming completion:

```bash
python scripts/validate_vault.py OUTPUT_ROOT/期末复习 --index-dir OUTPUT_ROOT/.course_index
```

Use this checklist when validating manually or interpreting script warnings:

| Check | Pass condition |
|---|---|
| Useful links | Each chapter overview has at least 3 meaningful wikilinks. |
| Concrete links | No placeholder link names like `<...>` or `核心概念A`. |
| Consistent names | Repeated concepts use the same link target. |
| Not overlinked | Ordinary words are not wrapped in links. |
| No prompt leakage | Internal skill instructions do not appear in notes. |
| Existing links preserved | Existing vault links were not removed or renamed without a reason. |

## Source and provenance vocabulary

Use user-facing labels that make evidence status clear without cluttering every sentence.

| Label | Use for | Notes |
|---|---|---|
| `本地权威资料` | teacher PPT, textbook, official handout, syllabus, standard/manual required by the course | Highest authority for scope, definitions, formulas, and chapter structure. |
| `课堂/用户笔记` | user's notes, annotations, “老师说”, “重点”, weak-point markers | Strong classroom signal; preserve even when not found in slides. |
| `来源题/历史题` | past papers, official review questions, homework, quizzes, assignments, question banks | Strongest signal for exam style and repeated topics. |
| `既有笔记` | existing Markdown/Obsidian vault content and prior organization decisions | Preserve during updates unless explicitly redesigned or corrected by higher authority. |
| `外部补充` | web, papers, other textbooks, external references | Use only for local gaps and mark clearly. |
| `模型推断/待核验` | model inference or prior knowledge without direct source support | Never present as certain course fact. |

Use evidence-status labels consistently:

- `明确依据`: a local source directly supports the content.
- `间接支持`: local sources support the idea but not the exact wording.
- `来源冲突`: local sources disagree, or source answer conflicts with teacher PPT, textbook, official handout, syllabus, or user-note material.
- `提取存疑`: OCR/PPT/table/formula extraction may be distorted.
- `待核验`: more checking is needed before treating it as reliable.
- `外部补充`: external material, subordinate to local course sources.

## Global files

### `00_总目录.md`

Include links to global files, chapter folders, source-question files, and final practice files.

### `00_资料索引.md`

Summarize source files by role:

| 文件 | 来源角色 | 覆盖章节 | 定位信息 | 提取质量 | 更新状态 | 备注 |
|---|---|---|---|---|---|---|

Use `定位信息` for page/slide/heading/question-number references when available. Use `更新状态` for values such as `unchanged`, `new_source`, `changed_source`, `impacted_chapter`, `needs_review`, or a Chinese equivalent.

### `00_术语索引.md`

List stable reusable terms and where they appear:

| 术语 | 主要章节 | 相关链接 | 来源信号 |
|---|---|---|---|

### `00_已有题目索引.md`

Use when source questions exist. Keep this as the inventory and routing table; detailed answers go in `00_来源题逐题解析.md`.

### `00_题目覆盖与笔记补强.md`

Track how source questions changed the notes. B-D items must either be written back into chapter files or logged as unresolved.

### `00_外部资料补充.md`

Use only when external search/sources were used. Keep external material separate and clearly subordinate to local course materials.

## Chapter organization

Each chapter should stand alone and link back to the whole vault.

### `01_章节总览.md`

Include:

- 用途
- 本章复习入口
- 本章概念卡片
- 本章知识主线
- 和前后章节的关系
- 本章考试策略
- 资料依据
- 不确定内容

### `02_核心概念.md`

Include:

- 概念卡片入口
- 必背概念 table: 概念 / 核心意思 / 复习要求
- 概念层级或 relationship diagram when helpful
- 容易被问成什么
- 不确定内容

### Dynamic `03_...` file

Use the course-type-specific file selected above. Include structures that match the discipline: formulas/models, theories/arguments, timelines, rules/applicability, or case mechanisms.

### `04_易混淆点.md`

Use comparison tables:

| 容易混淆的点 | 怎么区分 | 典型错误 |
|---|---|---|

### `05_典型考法.md`

Include common question forms, answer skeletons, scoring focus, and source links:

| 考法 | 常见问法 | 答题骨架 | 对应材料 |
|---|---|---|---|

### `06_自测题.md`

Include checkable questions appropriate to the course type:

- 名词解释
- 简答题
- 对比题
- 流程/模型题 where relevant
- 时间线/论述/案例/规则适用题 where relevant
- 计算/推导题 where relevant
- 自查答案方向

## Concept cards

Use concept cards for reusable, stable concepts only. Avoid over-splitting.

```markdown
# 概念名

## 用途
## 所属章节
## 核心定义
## 小白理解
## 为什么重要
## 适用条件
## 易错点
## 可能考法
## 相关链接
```

## Source marking

Keep source mapping centralized.

### `资料依据`

```markdown
## 资料依据

| 内容 | 主要依据 | 定位 | 依据级别 | 证据状态 |
|---|---|---|---|---|
```

Examples for `依据级别`: `本地权威资料`, `课堂/用户笔记`, `来源题/历史题`, `既有笔记`, `外部补充`, `模型推断/待核验`.

Examples for `证据状态`: `明确依据`, `间接支持`, `来源冲突`, `提取存疑`, `待核验`, `外部补充`.

### `不确定内容`

Use when local sources are incomplete, contradictory, unreadable, extraction is distorted, or existing vault content should be preserved but cannot yet be verified.

Prefer structured entries:

```markdown
## 不确定内容

### [issue]

- 影响内容：...
- 相关来源：...
- 冲突/存疑原因：...
- 当前处理：保留原文 / 暂按某来源写入 / 标为外部补充 / 暂不写入正文
- 下次核验：...
```

Short bullet examples are acceptable when the issue is simple:

```markdown
- PPT 文本提取中该公式符号有错位，当前笔记只保留模型思路；完整推导建议回到 PPT 原图核对。
- 用户笔记中写到 xxx，但老师 PPT 中没有找到明确对应内容；当前按课堂补充保留，考前建议确认。
```

If uncertain, retain existing content and add a caution note rather than deleting or replacing it.

### `外部资料标记`

```markdown
## 外部资料标记

以下内容来自外部检索，用于补充理解；考试时仍以老师 PPT、教材和课堂要求为准。

| 补充点 | 外部依据 | 写入位置 |
|---|---|---|
```

In the body, use light labels only when necessary:

```markdown
> 【外部补充】...
```
