
```
---
description: 三个项目（admin-fe/be、ticketing-system）Git 提交流程 - commit、push、合并到 base 并推送
alwaysApply: false
globs:
---

# 三个项目 Git 提交流程（按 rules 执行）

当用户要求「按 rules 提交」「完成后续操作」「合并到 base」时，按本流程对 **三个项目** 依次执行。

## 一、项目与分支约定

| 项目 | 仓库路径 | 主分支 | Base/测试分支 | 新功能从主分支拉取 |
|------|----------|--------|----------------|---------------------|
| admin 前端 | `gds-order-admin-fe` | `main` | `develop/base` | 从 main 创建 feature |
| admin 后端 | `gds-order-admin-be` | `master` | `base` | 从 master 创建 feature |
| 出票系统 | `gds-ticketing-system` | `master` | `develop/base_v5_jdk21`| 从 master 创建 feature |

- **功能分支命名（必须遵守）**：`feature/yyyyMMdd_功能简述`，例如 `feature/20250128_adminOptimization`；不得随意命名。
- **FE 新功能分支必须从 main 创建，不要从 develop/base 创建。**

## 二、流程概览

1. **Commit**：在各项目功能分支上提交当前更改。
2. **Push**：推送功能分支到远程；**第一次 push 时**顺带创建指向**主分支**的 Merge Request（GitLab push options）。
3. **Checkout base**：签出并更新各项目的 base 分支（ticketing-system 用 master）。
4. **Merge to base**：将功能分支合并到 base
5. **Push base**：推送 base 到远程。

以下命令均使用 **PowerShell**，路径与分支名按上表；`<FEATURE_BRANCH>` 需替换为实际功能分支名（如 `feature/20250128_adminOptimization`）。

- **分支命名（必须遵守）**：功能分支必须按 `feature/yyyyMMdd_功能简述` 命名，例如 `feature/20250128_adminOptimization`。
- **Git commit（必须遵守）**：commit 信息使用**英文**书写（如 `feat: add order list filter`）。
- **命令连接（必须遵守）**：多条 git 命令用**分号 `;`** 连接，不要使用 `&&`。

**必须禁用的操作**（禁止执行，以免破坏历史或协作）：

| 禁止操作 | 说明 |
|----------|------|
| **git rebase**（含 `rebase` 已 push 的分支） | 重写提交历史，导致与他人分支不一致、重复冲突；本流程一律使用 **merge**，不用 rebase。 |
| **git push --force / -f** | 强制覆盖远程分支，可能丢失他人或自己的提交。 |
| **git push --force-with-lease** | 同样会改写远程历史，本流程禁止使用。 |
| **直接向 main / master / base 推送** | 必须通过 MR 合并到主分支，或按流程 merge 到 base 后再 push；禁止绕过流程直接 push 到保护分支。 |
| **删除或重置 main、master、develop/base 等共享分支** | 禁止删除、`reset --hard` 到远程已存在的共享分支。 |
| **在已 push 的功能分支上做 amend 后 force push** | 等同于改写历史，禁止；若有新修改请新 commit 再 push。 |

---

## 三、分步命令（三个项目分别执行）

### 1. Commit（在各自功能分支上）

```powershell
# 1) admin-fe
cd D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git status
git add <需要提交的文件>
git commit -m "feat: short description"

# 2) admin-be
cd d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git status
git add <需要提交的文件>
git commit -m "feat: short description"

# 3) ticketing-system
cd D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git status
git add <需要提交的文件>
git commit -m "feat: short description"
```

### 2. Push 功能分支（第一次 push 时创建到主分支的 MR）

```powershell
# 1) admin-fe：主分支 main，push 时创建 MR target=main
cd D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git push -u origin <FEATURE_BRANCH> -o merge_request.create -o merge_request.target=main -o merge_request.remove_source_branch=false

# 2) admin-be：主分支 master，push 时创建 MR target=master
cd d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git push -u origin <FEATURE_BRANCH> -o merge_request.create -o merge_request.target=master -o merge_request.remove_source_branch=false

# 3) ticketing-system：主分支 master，push 时创建 MR target=master
cd D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git push -u origin <FEATURE_BRANCH> -o merge_request.create -o merge_request.target=master -o merge_request.remove_source_branch=false
```

若该分支已 push 过，只需普通 push：`git push origin <FEATURE_BRANCH>`，无需带 `-o` 选项。

### 3. Checkout base 并拉取最新

```powershell
# 1) admin-fe：base 为 develop/base
cd D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git fetch origin; git checkout develop/base; git pull origin develop/base

# 2) admin-be：base 为 base
cd d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git fetch origin; git checkout base; git pull origin base

# 3) ticketing-system：无 base，使用 master
cd D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git fetch origin; git checkout master; git pull origin master
```

### 4. Merge 功能分支到 base

```powershell
# 1) admin-fe
cd D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git merge <FEATURE_BRANCH>

# 2) admin-be
cd d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git merge <FEATURE_BRANCH>

# 3) ticketing-system
cd D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git merge <FEATURE_BRANCH>
```

### 5. Push base（或 master）

```powershell
# 1) admin-fe
cd D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git push origin develop/base

# 2) admin-be
cd d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git push origin base

# 3) ticketing-system
cd D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git push origin master
```

---

## 四、执行顺序与注意点

- 按 **fe → be → ticketing-system** 顺序执行，避免漏项目。
- **第一次 push** 时带 `-o merge_request.create -o merge_request.target=主分支` 会在 GitLab 上自动创建指向主分支的 MR；若远程非 GitLab 或不支持 push options，可去掉 `-o` 参数，仅执行 `git push -u origin <FEATURE_BRANCH>`。
- 若某项目无改动，可跳过该项目的 commit，但 push 功能分支、checkout base、merge、push base 仍建议按上表执行，保证三端一致。
- 合并冲突时：在对应项目内解决冲突后 `git add`、`git commit`，再执行该项目的 `git push origin <base或master>`。
- `git commit -m "..."` 使用英文，简短单行；多行说明可用 `-m "feat: title" -m "body"`。命令链用分号 `;` 连接，不用 `&&`。

---

## 五、一键脚本参考（PowerShell，替换 `<FEATURE_BRANCH>`）

```powershell
$branch = "feature/20250128_adminOptimization"  # 改为实际分支名

# === admin-fe ===
Set-Location D:\Users\zhaorun\IdeaProjects\gds-order-admin-fe
git push -u origin $branch -o merge_request.create -o merge_request.target=main -o merge_request.remove_source_branch=false
git fetch origin; git checkout develop/base; git pull origin develop/base
git merge $branch
git push origin develop/base

# === admin-be ===
Set-Location d:\Users\zhaorun\IdeaProjects\gds-order-admin-be
git push -u origin $branch -o merge_request.create -o merge_request.target=master -o merge_request.remove_source_branch=false
git fetch origin; git checkout base; git pull origin base
git merge $branch
git push origin base

# === ticketing-system ===
Set-Location D:\Users\zhaorun\IdeaProjects\gds-ticketing-system
git push -u origin $branch -o merge_request.create -o merge_request.target=master -o merge_request.remove_source_branch=false
git fetch origin; git checkout master; git pull origin master
git merge $branch
git push origin master
```

（执行前请先在各项目功能分支上完成 `git add` 与 `git commit`。）
```
