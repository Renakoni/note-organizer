# Note Organizer

_Exam in three days, and your materials are scattered across slides, PDFs, notes, and question banks? This skill helps Claude turn the mess into a Markdown note folder you can actually study from._

---

## Installation

Install the prerequisite skills first, then install this skill.

### 1. Install Claude official document skills

Note Organizer needs document skills to read PDF, Word, and PowerPoint materials. Install Anthropic's official `document-skills`, which includes `pdf`, `docx`, `pptx`, and `xlsx`.[^1]

In Claude Code, add the official skills marketplace first:

```text
/plugin marketplace add anthropics/skills
```

Then install the document skills:

```text
/plugin install document-skills@anthropic-agent-skills
```

### 2. Install humanizer

`humanizer` is used for final prose polishing after the content is already correct. It is optional, but recommended.

Repository: <https://github.com/blader/humanizer>

```bash
git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer
```

### 3. Install markdown-mermaid-writing

`markdown-mermaid-writing` helps with Markdown structure, relationship maps, and document organization. Note Organizer does not require README files or notes to use Mermaid, but this skill is useful for complex knowledge maps.

Source repository: <https://github.com/K-Dense-AI/scientific-agent-skills>

If you only want this skill, use sparse checkout:

```bash
git clone --filter=blob:none --sparse https://github.com/K-Dense-AI/scientific-agent-skills.git /tmp/scientific-agent-skills
cd /tmp/scientific-agent-skills
git sparse-checkout set markdown-mermaid-writing
mkdir -p ~/.claude/skills
cp -R markdown-mermaid-writing ~/.claude/skills/markdown-mermaid-writing
```

If you already have the `markdown-mermaid-writing` skill, place it in Claude's skills directory:

```text
~/.claude/skills/markdown-mermaid-writing/
```

### 4. Install Note Organizer

Clone this repository into Claude's skills directory:

```bash
git clone https://github.com/Renakoni/note-organizer.git ~/.claude/skills/note-organizer
```

The final structure should look like this:

```text
~/.claude/skills/note-organizer/
├─ SKILL.md
├─ README.md
├─ README.en.md
├─ references/
└─ scripts/
```

After installation, restart Claude Code or start a new session.

## Quick start

Put your materials in one folder, then call the skill explicitly:

```text
/note-organizer
The materials are in ./material. Please organize them into a review note library.
```

You can also be more specific:

```text
/note-organizer
This folder contains teacher PPTs, textbook excerpts, my class notes, and several past exam papers. Please organize them into a Markdown note library, and keep source questions separate from generated questions.
```

You can also omit the slash command and simply ask Claude to organize notes or review materials. Claude should call this skill when the task fits.

Claude will first scan the materials, identify existing questions, infer chapters and source roles, then ask for one structure confirmation. After that, it will continue in batches.

## What this skill does

Note Organizer is a Claude Skill for the moment when you technically have all the materials, but no clear place to start. It works with teacher slides, textbook excerpts, PDFs, Word documents, PowerPoint files, personal notes, senior-student notes, homework questions, past exams, and question banks.

It does not squeeze everything into one long summary. It first sorts out the sources, infers the chapter structure, extracts existing questions, builds a local index, and then writes chapter-based Markdown notes you can keep editing.

Obsidian is the recommended way to open the generated folder. The notes are plain Markdown and include `[[wikilinks]]`, so you can keep reviewing, editing, and jumping between related ideas in Obsidian. VS Code, GitHub, and other Markdown tools work too.

## Recommended workflow

1. Put all materials in one folder.
2. Use meaningful file names when possible, such as `teacher_ppt`, `user_notes`, `past_exam`, or `question_bank`.
3. Ask Claude to scan the materials, extract existing questions, infer chapters, and propose an output structure.
4. Check whether the chapter structure and source roles look right.
5. Let Claude generate chapter notes, source-question analysis, and strengthening logs in batches.
6. Review `00_资料缺口与待确认.md` and `00_题目覆盖与笔记补强.md` at the end.

## Good use cases

- Final exam review
- Graduate entrance exam, certification exam, or professional course review
- Turning teacher slides and textbooks into chapter notes
- Using question banks, homework, or past exams to check knowledge coverage
- Organizing long courses that need batching and resume support
- Strengthening an existing Markdown or Obsidian note library
- Building different note structures for literature, history, law, medicine, engineering, computer science, and other subjects

## Output files

A full run may produce files such as:

- `00_总目录.md`
- `00_项目状态.md`
- `00_资料索引.md`
- `00_章节进度表.md`
- `00_术语索引.md`
- `00_已有题目索引.md`
- `00_题目覆盖与笔记补强.md`
- `00_资料缺口与待确认.md`
- `00_检索日志.md`
- `00_全书知识关系与复习路线.md`
- `00_考前速记与最后冲刺.md`
- `00_来源题逐题解析.md`
- `00_自建题库.md`
- per-chapter overview, core concepts, knowledge structure, confusing points, question patterns, and self-tests
- Obsidian `[[wikilinks]]` for stable concepts
- `.course_index/` local index files

The exact files depend on the materials. If there are no existing questions, the skill will not force a source-question analysis file. If external materials are used, they are marked separately.

## Key ideas

### Existing questions first

The skill extracts existing questions during the first scan, including homework, review questions, thinking questions, past exams, assignments, and question banks. The notes are guided by real questions instead of generic summaries.

### Source hierarchy

Teacher slides, textbooks, class notes, question banks, senior-student notes, and external sources are handled separately. Exam-facing wording should follow teacher slides, textbooks, and class notes first.

### Coverage checks

After chapter notes are drafted, the skill checks whether existing questions are covered. Gaps are written to `00_题目覆盖与笔记补强.md` or `00_资料缺口与待确认.md`.

### Subject-aware templates

Different subjects need different note structures. STEM courses may use formula/model workflows. Literature history may use timelines. Law may use rules and applicability conditions. Case-based courses may use case mechanisms and handling flows.

### Local lightweight indexing

For whole courses or folders, the skill builds a `.course_index/` folder to track files, chapters, questions, terms, and progress. It uses auditable local search and chapter packs by default, not a mandatory heavy RAG system.

### Bounded external supplements

If local materials are incomplete, the skill can add external supplements at the end. External content is marked separately and should not override teacher slides, textbooks, or class notes.

## Notes

- Scanned PDFs, formula screenshots, and complex PPT layouts may need manual checking against the original files.
- `coverage_check.py` is a conservative local support check, not a final grader.
- External sources are for additional understanding. Course materials remain the authority for exam wording.
- Large Markdown generation jobs are easier to run in the foreground so Claude can ask for file-write approval when needed.

## Good fit and poor fit

Good fit:

- Course material organization
- Exam review
- Question-bank-driven note strengthening
- Markdown or Obsidian note libraries
- Long-course batch organization

Poor fit:

- Asking one quick fact from a PDF
- Fully replacing human review of formulas, figures, or scanned documents
- Treating web search results as the only course authority
- Building a full vector database or complex research RAG platform

## License and dependency notes

This project is released under the MIT License. See [LICENSE](LICENSE).

This skill does not copy, modify, or redistribute the `pdf`, `docx`, or `pptx` document skills. Install those skills from their own sources and follow their own licenses.

[^1]: Anthropic. `anthropics/skills`: Public repository for Agent Skills. https://github.com/anthropics/skills
