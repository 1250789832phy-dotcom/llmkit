# Two-Repository Documentation Accuracy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify retry behavior in LLMKit and process/environment configuration behavior in SafeDesk without changing runtime code.

**Architecture:** Modify only the two repository README files. The wording will mirror the existing `LLMClient.complete()`/`stream()` implementation and SafeDesk's startup environment handling, so no new APIs or dependencies are introduced.

**Tech Stack:** Markdown documentation, existing Python `pytest` suites, GitHub Actions matrix.

## Global Constraints

- Do not edit library implementation, public signatures, or test assertions.
- Do not modify or remove the original learning project.
- Preserve the LLMKit Function Calling roadmap item as unimplemented.
- Use commit identity `phy <299836398+1250789832phy-dotcom@users.noreply.github.com>`.
- Verify both repositories locally before claiming completion.

### Task 1: Clarify LLMKit Retry and Streaming Documentation

**Files:**
- Modify: `E:\科研\llmkit\README.md` in the “重试和退避” and “流式输出” sections.

**Interfaces:**
- Consumes: Existing `LLMClient.complete()` retry parameters and `LLMClient.stream()` behavior.
- Produces: README wording that distinguishes automatic retries from caller-managed streaming recovery.

- [ ] **Step 1: Add the behavior note**

Add after the retry interval example:

```markdown
`retries` 表示首次调用之后允许的重试次数。自动重试仅适用于
`complete()`；`stream()` 直接返回 Provider 的流，不会自动重试，
流式连接失败时请由业务层决定是否重新建立连接。
```

- [ ] **Step 2: Check the focused diff**

Run:

```powershell
git -C E:\科研\llmkit diff --check
git -C E:\科研\llmkit diff -- README.md
```

Expected: only the retry/streaming explanation is added, with no whitespace errors.

### Task 2: Clarify SafeDesk Environment Variable Lifetime

**Files:**
- Modify: `E:\科研\safedesk\README.md` in the model configuration section.

**Interfaces:**
- Consumes: Existing `SAFE_DESK_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_BASE_URL` startup behavior.
- Produces: PowerShell and Bash commands that clear those variables and return to mock mode.

- [ ] **Step 1: Add startup lifetime and reset commands**

Add after the existing environment-variable explanation:

```markdown
这些变量只会在服务进程启动时读取；修改变量后必须停止并重新启动服务。
若要在当前终端恢复默认的 mock planner：
```

Add the following PowerShell block:

```powershell
Remove-Item Env:SAFE_DESK_MODEL, Env:OPENAI_API_KEY, Env:OPENAI_MODEL, Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --reload --port 8000
```

Add the following Bash block:

```bash
unset SAFE_DESK_MODEL OPENAI_API_KEY OPENAI_MODEL OPENAI_BASE_URL
python -m uvicorn apps.api.main:app --reload --port 8000
```

- [ ] **Step 2: Check the focused diff**

Run:

```powershell
git -C E:\科研\safedesk diff --check
git -C E:\科研\safedesk diff -- README.md
```

Expected: only the model configuration guidance changes, with no whitespace errors.

### Task 3: Verify, Commit, Push, and Inspect CI

**Files:**
- No additional source files.
- Existing design and plan records remain documentation-only commits in LLMKit.

- [ ] **Step 1: Run full local tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

from each repository. Expected: zero failures and zero errors.

- [ ] **Step 2: Commit with the required identity**

Use separate commits:

```powershell
git -C E:\科研\llmkit -c user.name=phy -c user.email=299836398+1250789832phy-dotcom@users.noreply.github.com commit -am "docs: clarify retry and streaming behavior"
git -C E:\科研\safedesk -c user.name=phy -c user.email=299836398+1250789832phy-dotcom@users.noreply.github.com commit -am "docs: clarify environment variable lifetime"
```

- [ ] **Step 3: Push both main branches**

Run `git push origin main` for each repository. If the direct GitHub endpoint is unavailable, use the previously verified one-command `http.curloptResolve` override without changing global configuration.

- [ ] **Step 4: Verify latest-head CI**

Query the Actions run whose `head_sha` equals each pushed commit. Expected: six completed successful jobs per repository for Ubuntu/Windows × Python 3.11/3.12/3.13.
