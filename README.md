# 笔记整理Skill

_三天后考试，课件还没看，PDF 还没翻，笔记散得像案发现场？把资料文件夹交给它，它会先理清章节、题目和重点，再整理成一套能直接打开复习的 Markdown 笔记。_

English version: [README.en.md](README.en.md)

---

## 安装

安装前置 skills，然后安装本 skill。

### 1. 安装 Claude 官方文档 skills

笔记整理需要读取 PDF、Word 和 PowerPoint 资料。先安装 Anthropic 官方 `document-skills`，其中包含 `pdf`、`docx`、`pptx` 和 `xlsx`。[^1]

在 Claude Code 中先添加官方 skills marketplace：

```text
/plugin marketplace add anthropics/skills
```

然后安装文档 skills：

```text
/plugin install document-skills@anthropic-agent-skills
```

### 2. 安装推荐辅助 skills

完整体验需要 `humanizer` 和 `markdown-mermaid-writing`：

- `humanizer`：用于在内容正确后做文字润色，让最终笔记读起来更自然。
- `markdown-mermaid-writing`：用于知识关系图、章节结构图和复习路线图。没有它也能整理笔记，但完整形态需要它。

本仓库提供了安装脚本：

```bash
bash tools/install-recommended-skills.sh
```

脚本会安装：

- `humanizer`：<https://github.com/blader/humanizer>
- `markdown-mermaid-writing`：来自 <https://github.com/K-Dense-AI/scientific-agent-skills>

如需手动安装，可参考脚本内容。

### 3. 安装笔记整理

把本仓库放入 Claude 的 skills 目录：

```bash
git clone https://github.com/Renakoni/note-organizer.git ~/.claude/skills/note-organizer
```

也可以手动复制目录，最终结构应类似：

```text
~/.claude/skills/note-organizer/
├─ SKILL.md
├─ README.md
├─ references/
└─ scripts/
```

安装完成后，重启 Claude Code 或开启一个新会话。

## 快速使用

把资料放进一个文件夹，然后显式调用 skill：

```text
/note-organizer
资料都在 ./material，帮我整理成一套复习笔记。
```

也可以说得更具体：

```text
/note-organizer
这个文件夹里有老师 PPT、教材摘录、我的课堂笔记和几份历年题。请整理成 Markdown 笔记库，题目和自建题要分开。
```

也可以不写 slash command，直接说“帮我整理笔记”或“帮我整理复习资料”。Claude 会在合适时自动调用这个 skill。

Claude 会先扫描资料、识别已有题目、推断章节和资料角色，然后给出一次结构确认。确认后，它会继续分批生成笔记。

## 项目简介

笔记整理是一个 Claude Skill，用来处理那种“资料都有，但不知道从哪里开始看”的学习场景。老师课件、教材摘录、PDF、Word 文档、PPT、个人课堂笔记、学长学姐资料、课后习题、历年试题和题库，都可以一起交给它整理。

它不会把所有资料压成一篇长总结。它会先梳理资料来源，再推断章节结构，提取已有题目，建立索引，然后按章节生成可以继续维护的 Markdown 笔记。

推荐用 Obsidian 打开整理后的文件夹。生成的笔记是普通 Markdown 文件，里面会带有 `[[双链]]`，适合在 Obsidian 里继续复习、补充和跳转。你也可以用 VS Code、GitHub 或其他 Markdown 工具查看。

## 推荐工作流

1. 把资料放进同一个文件夹。
2. 尽量保留有意义的文件名，例如 `teacher_ppt`、`user_notes`、`past_exam`、`question_bank`。
3. 让 Claude 先扫描资料、提取已有题目、推断章节，并规划输出结构。
4. 检查章节结构和资料角色有没有明显错误。
5. 让 Claude 分批生成章节笔记、题目解析和补强记录。
6. 最后查看 `00_资料缺口与待确认.md` 和 `00_题目覆盖与笔记补强.md`。

## 适合哪些场景

- 期末考试复习
- 考研、资格考试或专业课复习
- 把老师课件和教材整理成章节笔记
- 用题库、课后习题或历年题反查知识点覆盖情况
- 整理较长课程，并且希望能分批推进、断点续跑
- 把已有 Markdown 或 Obsidian 笔记补成完整的复习系统
- 为文学、历史、法学、医学、工科、计算机等不同学科建立合适的笔记结构

## 它会生成什么

一次完整整理通常会生成这些文件：

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
- 每章的章节总览、核心概念、知识框架、易混淆点、典型考法和自测题
- 稳定概念的 Obsidian `[[双链]]`
- `.course_index/` 本地索引文件

实际文件会根据资料情况调整。没有已有题目时，不会强行生成来源题解析；使用外部资料时，会额外生成或更新外部资料标记。

## 核心特点

### 题目优先

Skill 会在第一轮扫描里提取已有题目，包括课后习题、复习题、思考题、历年题、考试题、作业题和题库。这样整理出来的笔记不是泛泛概括，而是被真实题目牵引。

### 来源分级

老师课件、教材、课堂笔记、题库、学长学姐资料和外部资料会分开处理。考试相关表述优先以老师课件、教材和课堂笔记为准。

### 题目覆盖检查

整理完章节后，Skill 会根据已有题目检查笔记是否覆盖到位。缺口会写入 `00_题目覆盖与笔记补强.md` 或 `00_资料缺口与待确认.md`，方便后续补强。

### 适配不同学科

不同学科不应该套同一种模板。理工科可以使用公式模型流程，文学史可以使用时间线与脉络，法学可以使用规则条文与适用条件，案例型课程可以使用案例机制与处理流程。

### 本地轻量索引

对于整门课程或资料文件夹，Skill 会建立 `.course_index/` 本地索引，用来记录文件、章节、题目、术语和处理进度。默认使用可审计的本地检索和章节包，不强制搭建复杂 RAG 系统。

### 外部资料有边界

如果本地资料缺失，Skill 可以在最后阶段补充外部资料。外部资料会单独标记，不会覆盖老师课件、教材和课堂笔记。

## 注意事项

- 扫描版 PDF、公式截图或排版复杂的 PPT 可能提取不完整，需要回看原文件。
- `coverage_check.py` 是保守的本地支持度检查，不是最终判卷器。
- 外部资料只用于补充理解，考试表述仍应以本地课程资料为准。
- 大量写入 Markdown 文件时，建议在前台运行 Claude，以便及时批准文件写入。

## 适合与不适合

适合：

- 课程资料整理
- 考试复习
- 题库驱动的知识点补强
- Markdown 或 Obsidian 笔记库建设
- 长课程的分批整理

不适合：

- 只想简单问一个 PDF 里的事实
- 完全自动替代人工核对公式、图表和扫描件
- 把外部搜索结果当作课程唯一依据
- 需要完整语义向量数据库或复杂 RAG 平台的研究知识库

## 许可证与依赖说明

本项目使用 MIT License，详见 [LICENSE](LICENSE)。

本 skill 不复制、修改或再分发 `pdf`、`docx`、`pptx` 等文档处理 skills。请按这些 skills 各自的来源和许可单独安装。

[^1]: Anthropic. `anthropics/skills`: Public repository for Agent Skills. https://github.com/anthropics/skills
