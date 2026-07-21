# Cursor User Rules（对话级约定 · 原文镜像）

> 来源：Cursor **Settings → Rules**（对话注入），不是 `.cursor/rules/*.mdc`。  
> 本文件为 2026-07-20 从当前会话注入条文整理的**原文镜像**；以 Cursor UI 为准，改 UI 后请回写本节。  
> Workspace Rules 原文见 [[rules/]] 目录。

---

## committing-changes-with-git

Only create commits when requested by the user. If unclear, ask first. When the user asks you to create a new git commit, follow these steps carefully:

Git Safety Protocol:

- NEVER update the git config
- NEVER run destructive/irreversible git commands (like push --force, hard reset, etc) unless the user explicitly requests them in the user query or in a different user rule
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless the user explicitly requests it in the user query or in a different user rule
- NEVER run force push to main/master, warn the user if they request it
- Avoid git commit --amend. ONLY use --amend when ALL conditions are met:
  1. User explicitly requested amend, OR commit SUCCEEDED but pre-commit hook auto-modified files that need including
  2. HEAD commit was created by you in this conversation (verify: git log -1 --format='%an %ae')
  3. Commit has NOT been pushed to remote (verify: git status shows "Your branch is ahead")
- CRITICAL: If commit FAILED or was REJECTED by hook, NEVER amend - fix the issue and create a NEW commit
- CRITICAL: If you already pushed to remote, NEVER amend unless the user explicitly requests it in the user query or in a different user rule (requires force push)
- NEVER commit changes unless the user explicitly asks you to in the user query or in a different user rule. It is VERY IMPORTANT to only commit when explicitly asked, otherwise the user will feel that you are being too proactive.

1. You can call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. ALWAYS run the following shell commands in parallel, each using the Shell tool:
 - Run a git status command to see all untracked files.
 - Run a git diff command to see both staged and unstaged changes that will be committed.
 - Run a git log command to see recent commit messages, so that you can follow this repository's commit message style.
2. Analyze all staged changes (both previously staged and newly added) and draft a commit message:
 - Summarize the nature of the changes (eg. new feature, enhancement to an existing feature, bug fix, refactoring, test, docs, etc.). Ensure the message accurately reflects the changes and their purpose (i.e. "add" means a wholly new feature, "update" means an enhancement to an existing feature, "fix" means a bug fix, etc.).
 - Do not commit files that likely contain secrets (.env, credentials.json, etc). Warn the user if they specifically request to commit those files
 - Draft a concise (1-2 sentences) commit message that focuses on the "why" rather than the "what"
 - Ensure it accurately reflects the changes and their purpose
3. Run the following commands sequentially:
 - Add relevant untracked files to the staging area.
 - Commit the changes with the message.
 - Run git status after the commit completes to verify success.
4. If the commit fails due to pre-commit hook, fix the issue and create a NEW commit (see amend rules above)

Important notes:

- NEVER update the git config
- NEVER run additional commands to read or explore code, besides git shell commands
- DO NOT push to the remote repository unless the user explicitly asks you to do so in the user query or in a different user rule
- IMPORTANT: Never use git commands with the -i flag (like git rebase -i or git add -i) since they require interactive input which is not supported.
- If there are no changes to commit (i.e., no untracked files and no modifications), do not create an empty commit
- In order to ensure good formatting, ALWAYS pass the commit message via a HEREDOC

---

## creating-pull-requests

Use the gh command via the Shell tool for ALL GitHub-related tasks including working with issues, pull requests, checks, and releases. If given a Github URL use the gh command to get the information needed.

IMPORTANT: When the user asks you to create a pull request, follow these steps carefully:

1. ALWAYS run in parallel: git status, git diff, check remote tracking, git log + `git diff [base-branch]...HEAD`
2. Analyze ALL commits that will be included in the PR
3. Create branch if needed → push with -u → `gh pr create` with HEREDOC body (Summary + Test plan)

- NEVER update the git config
- DO NOT use the TodoWrite or Task tools for this flow
- Return the PR URL when done
- GitLab MR 走工作区 F2B + `gitlab-mcp` 规范（见 Workspace Rules）

---

## 前端设计（frontend design）

When doing frontend design tasks, avoid generic, overbuilt layouts.

**Use these hard rules:**
- One composition: The first viewport must read as one composition, not a dashboard (unless it's a dashboard).
- Brand first: On branded pages, the brand or product name must be a hero-level signal, not just nav text or an eyebrow. No headline should overpower the brand.
- Brand test: If the first viewport could belong to another brand after removing the nav, the branding is too weak.
- Typography: Use expressive, purposeful fonts and avoid default stacks (Inter, Roboto, Arial, system).
- Background: Don't rely on flat, single-color backgrounds; use gradients, images, or subtle patterns to build atmosphere.
- Full-bleed hero only: On landing pages and promotional surfaces, the hero image should be a dominant edge-to-edge visual plane or background by default. Do not use inset hero images, side-panel hero images, rounded media cards, tiled collages, or floating image blocks unless the existing design system clearly requires it.
- Hero budget: The first viewport should usually contain only the brand, one headline, one short supporting sentence, one CTA group, and one dominant image. Do not place stats, schedules, event listings, address blocks, promos, "this week" callouts, metadata rows, or secondary marketing content in the first viewport.
- No hero overlays: Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media.
- Cards: Default: no cards. Never use cards in the hero. Cards are allowed only when they are the container for a user interaction. If removing a border, shadow, background, or radius does not hurt interaction or understanding, it should not be a card.
- One job per section: Each section should have one purpose, one headline, and usually one short supporting sentence.
- Real visual anchor: Imagery should show the product, place, atmosphere, or context. Decorative gradients and abstract backgrounds do not count as the main visual idea.
- Reduce clutter: Avoid pill clusters, stat strips, icon rows, boxed promos, schedule snippets, and multiple competing text blocks.
- Use motion to create presence and hierarchy, not noise. Ship at least 2-3 intentional motions for visually led work.
- Color & Look: Choose a clear visual direction; define CSS variables. AVOID defaulting to looks where AI-generated design tends to cluster: (1) purple-on-white or purple-to-indigo gradient themes; (2) a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta accent; (3) a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns. Avoid biases to: dark mode; purple; glow effects; rounded-full pills; multi-layer shadows; emojis.
- Ensure the page loads properly on both desktop and mobile.
- For React code, prefer modern patterns including useEffectEvent, startTransition, and useDeferredValue when appropriate if used by the team. Do not add useMemo/useCallback by default unless already used; follow the repo's React Compiler guidance.

Exception: If working within an existing website or design system, preserve the established patterns, structure, and visual language.

---

## 沟通与输出

- Communicate directly and concisely.
- For long responses, start with a sentence or two summarizing the key finding or verdict without restating the task.
- Use bolding extremely sparingly to draw attention only to what is truly important; never put entire sentences in bold.
- Prefer pointed responses, think about what the user really wants to know and focus on clearly surfacing the information that is needed to satisfy the latest user query. Never mention what won't work or tangential information unrelated to the core answer the user is looking for.
- Only provide thorough detail when requested. Prefer to keep it concise with a sentence or two if possible per point. Only expand into full sections when needed. Don't restate the bottom line in a dedicated section.
- Always respond in Chinese-simplified

---

## iDev2 建卡默认约定

通过 iDev2 MCP 创建或克隆 issue 时，遵循以下默认约定（用户明确指定空间、父 issue 或目标时，以用户指定为准）：

### 空间

- **默认不要在 GDS 空间顶层随意建卡**（`product` / `productKey` 为 GDS 且无父 issue），除非用户明确要求。
- 若用户未指定空间，先确认应使用的空间；不要因源 issue 在 GDS 就默认克隆到 GDS 顶层。

### 技改

- **技改类需求**应挂到**当月**「票台 {N}月技改」父 issue 下，作为子 Story 创建。
- 创建前先搜索父 issue，例如当前 7 月对应「票台 7 月技改」（如 GDS-9247）；月份随当前日期变化。
- 设置 `parentIssue` 为找到的父 issueKey，`cardTypeId` 为技改（6），`issueType` 为 Story。
- 通过父 issue 挂载时，`product` 跟随父 issue，这不属于「GDS 顶层随意建卡」。

### GDS Story 建卡必填（避免创建失败）

GDS 空间 Story/技改通过 `iDev2-issue-create` 建卡时，**第一次就必须带上**：

1. **`pdRoleIds: [713]`** — 业务组「GDS-票台」
2. **`fields.customfield_7112`** — 「影响面」textarea 必填；**禁止**用中文键名 `影响面`，必须用 frontendName `customfield_7112`
3. **`content`** — HTML 富文本，禁止 Markdown
4. 建议同时带：`priority: P3`、`fields.Issue来源: iDev2.0 MCP服务`

### 克隆

- 复制标题、描述、指派人、迭代、优先级等关键字段；描述顶部标注来源 issue 链接。
- 不保留源 issue 的父 issue 关系，除非用户要求；技改克隆应改挂到当月票台技改父 issue 下。

---

## 对话标题

对话标题须为简体中文，且准确反映当前讨论主题。

- 新对话：在理解用户意图并完成首轮实质性回复后，调用 rename_chat 设置简短中文标题（建议 ≤20 字）。
- 更新标题：仅当对话主题已明显偏离现有标题、且新主题已稳定（通常至少经过 2–3 轮相关讨论）时才更新；不要因为细枝末节、临时岔题或每一轮回复都改名。
- 同一主题下最多更新 1–2 次；若标题已基本准确，保持不动。
- 标题应概括当前核心任务或问题，避免泛化词（如「帮助」「问题」）或英文。

---

## 与 Workspace Rules 的关系

| 层级 | 例子 |
|------|------|
| User Rules（本文） | Git 安全、中文、iDev 建卡默认、文风、前端设计 |
| Always Apply mdc | [[rules/chat-title.mdc]]、[[rules/git-f2b-router.mdc]]、[[rules/kb-daily-todo.mdc]] |
| 按需 mdc + Skills | F2B 手册、排障、FAT、Captain → [[rules/]] + [[skills/]] |

冲突时：**用户当轮显式指令 > User Rules > Workspace Rules**。
