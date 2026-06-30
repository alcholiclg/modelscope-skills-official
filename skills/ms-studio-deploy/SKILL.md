---
name: ms-studio-deploy
description: >-
  将本地项目部署到 ModelScope 创空间 (Studio)。支持 Gradio、Streamlit、Docker、静态网站类型。
  覆盖创建、代码同步、部署、日志监控、明文/密文变量管理、自动诊断修复。
  当用户提到部署到 ModelScope、创空间、魔搭社区、魔搭、Studio 部署、Gradio 部署、Streamlit 部署、
  Docker 部署、FastAPI 部署、静态网站部署，或者想要把本地应用、Web 应用、API 服务发布到云端时使用。
  也适用于用户遇到创空间构建失败、运行错误需要排查日志、想要更新已部署的创空间、管理创空间明文或密文变量等场景。
  不适用于: Hub 仓库管理、模型/数据集操作、MCP/技能管理、模型训练、模型评测。
---

# ModelScope 创空间部署

> Verified live against ModelScope OpenAPI ｜ modelscope 1.37.1 / modelscope_hub 0.1.2 (2026-06-29)

将本地项目部署到 ModelScope 创空间。**本 Skill 以 OpenAPI 为事实来源**，`ms` CLI 作为等价便捷别名，`modelscope_hub.HubApi` 作为 API 优先的 Python 客户端，MCP 工具为可选项。

## 快速决策指南

```
用户想要...
│
├── 部署本地项目到创空间
│   └── 按下方「完整部署流程」10 步执行
│
├── 更新已部署的创空间
│   └── 修改代码 → git push → POST /studios/{o}/{r}/deploy（或 ms deploy）
│
├── 查看创空间状态/日志
│   └── GET /studios/{o}/{r}/logs/run（或 ms logs --log-type run）
│
├── 管理变量
│   ├── 明文变量：GET/POST/PUT/DELETE /studios/{o}/{r}/variables
│   └── 密文变量：GET/POST/PUT/DELETE /studios/{o}/{r}/secrets（或 ms secret ...）
│
└── 仓库文件管理 / 模型数据集操作
    └── hand off → ms-hub
```

## 前置条件

### 1. MODELSCOPE_API_KEY

整个流程依赖此令牌（API 认证、Git 推送、环境变量配置），必须最先确认。

```bash
# 1. 先检查环境变量
echo $MODELSCOPE_API_KEY

# 2. 如果为空，尝试从 git remote 中提取（可能之前配置过）
git remote -v 2>/dev/null | grep modelscope.cn
```

如果环境变量为空但 git remote 中包含形如 `https://oauth2:<token>@www.modelscope.cn/studios/...` 的地址，从中提取 `<token>` 作为 `MODELSCOPE_API_KEY`。
两者都没有时，引导用户：

1. 访问 https://modelscope.cn/my/myaccesstoken 获取令牌
2. `export MODELSCOPE_API_KEY=your_token`

### 2. 运行环境

```bash
pip install modelscope          # 同时获得 OpenAPI/SDK 与 ms CLI
```

OpenAPI 基础约定：

| 项目 | 值 |
|------|-----|
| **Base URL** | `https://modelscope.cn/openapi/v1` |
| **认证** | `Authorization: Bearer $MODELSCOPE_API_KEY` |
| **成功响应** | `{"success": true, "data": {...}, "request_id": "..."}` |
| **默认分支** | `master`（非 main） |

### 3. Git 环境

创空间代码通过 Git 同步，确保已安装 Git 并配置用户信息。

## 操作总览：OpenAPI（事实来源）↔ CLI ↔ Python

| 操作 | OpenAPI（事实来源） | ms CLI（等价别名） | `modelscope_hub.HubApi`（Python） | MCP 工具（可选） |
|------|---------------------|---------------------|-----------------------------------|------------------|
| 用户信息 | `GET /users/me` | `ms whoami` | `api.whoami()` | `getCurrentUser` |
| 创建创空间 | `POST /studios` | `ms create o/r --repo-type studio` | `api.create_repo("o/r", repo_type="studio", ...)` | `createStudio` |
| 获取详情 | `GET /studios/{o}/{r}` | `ms info o/r --repo-type studio` | `api.get_repo("o/r", repo_type="studio")` | `getStudio` |
| 部署/重启 | `POST /studios/{o}/{r}/deploy` | `ms deploy o/r --repo-type studio` | `api.deploy_repo("o/r")` | `deployStudio` |
| 停止 | `POST /studios/{o}/{r}/stop` | `ms stop o/r --repo-type studio` | `api.stop_repo("o/r")` | `stopStudio` |
| 日志 | `GET /studios/{o}/{r}/logs/{run\|build}` | `ms logs o/r --log-type run` | `api.get_repo_logs("o/r", log_type="run")` | `getStudioLogs` |
| 更新设置 | `PATCH /studios/{o}/{r}/settings` | `ms settings o/r --repo-type studio k=v` | `api.update_repo_settings("o/r","studio",**kw)` | `updateStudioSettings` |
| 查询可用硬件 | `GET /studios/hardware?sdk_type=gradio[&studio=o/r]` | 暂无 | 暂无 | `listHardware` |
| 查询 SDK 版本 | `GET /studios/sdk-versions?sdk_type=gradio` | 暂无 | 暂无 | `listSdkVersions` |
| 查询基础镜像 | `GET /studios/base-images` | 暂无 | 暂无 | `listBaseImages` |
| 列出明文变量 | `GET /studios/{o}/{r}/variables` | 暂无 | 暂无 | `listStudioVariables` |
| 添加明文变量 | `POST /studios/{o}/{r}/variables` | 暂无 | 暂无 | `addStudioVariable` |
| 更新明文变量 | `PUT /studios/{o}/{r}/variables` | 暂无 | 暂无 | `updateStudioVariable` |
| 删除明文变量 | `DELETE /studios/{o}/{r}/variables` | 暂无 | 暂无 | `deleteStudioVariable` |
| 列出密文变量 | `GET /studios/{o}/{r}/secrets` | `ms secret list o/r` | `api.list_secrets("o/r")` | `listStudioSecrets` |
| 添加密文变量 | `POST /studios/{o}/{r}/secrets` | `ms secret add o/r K V` | `api.add_secret("o/r","K","V")` | `addStudioSecret` |
| 更新密文变量 | `PUT /studios/{o}/{r}/secrets` | `ms secret update o/r K V` | `api.update_secret("o/r","K","V")` | `updateStudioSecret` |
| 删除密文变量 | `DELETE /studios/{o}/{r}/secrets` | `ms secret delete o/r K` | `api.delete_secret("o/r","K")` | `deleteStudioSecret` |

> **`HubApi` 是驱动 `ms` CLI 的同一引擎**，是 API 优先的 Python 入口：
> ```python
> from modelscope_hub import HubApi
> api = HubApi(); api.login("$MODELSCOPE_API_KEY")
> ```
> 注意它与旧版 `modelscope.hub.api.HubApi` 是两套类：旧版尚未打通 deploy/stop 等创空间方法，**新版 `modelscope_hub.HubApi` 已打通**（其 `deploy_repo`/`stop_repo`/`get_repo_logs`/密文变量 secret 系列默认 `repo_type="studio"`）。

> **MCP 工具（可选）** — 上表最后一列为 `studio-mcp` 服务提供的等价工具，语义与同行 OpenAPI 调用一致；agent 已配置该服务时可直接调用，无需配置时忽略此列。首次配置方法见文末附录。

## 完整部署流程

> 每步以 OpenAPI 为主，给出等价 CLI 一行命令。`${owner}`/`${repo}` 为创空间归属与名称。

### Step 1: 检查本地 Git 仓库

```bash
[ -d .git ] && git remote -v 2>/dev/null | grep modelscope.cn/studios
```

- 已有创空间远程地址 → 从 URL 提取 `owner` 和 `repo`，跳到 Step 3
- 没有 → 继续 Step 2

### Step 2: 分析项目并获取用户信息

#### 2.1 确定 SDK 类型

| 类型 | 检测条件 | 入口文件 | 备注 |
|------|----------|----------|------|
| `gradio` | `app.py` 导入 gradio | `app.py` | 按需查询 `sdk_version`, `base_image`, `hardware` |
| `streamlit` | `app.py` 使用 streamlit | `app.py` | 按需查询 `base_image`, `hardware` |
| `docker` | 存在 `Dockerfile` | `Dockerfile` | 端口必须 7860 |
| `static` | 存在 `index.html`（已构建） | `index.html` | 不支持构建步骤；不选择硬件 |

选择建议：`static` 不支持构建步骤，文件必须已构建；需构建的前端项目用 `docker`；不确定时用 `docker`。

> `docker` 类型需先在魔搭平台完成阿里云账号绑定并通过实名认证：https://modelscope.cn/docs/studios/docker ，否则无法构建镜像。

#### 2.2 获取用户信息

```bash
curl "https://modelscope.cn/openapi/v1/users/me" -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 等价 CLI： ms whoami
```

`repo` 从项目目录名或用户指定获取。

### Step 3: 创建或更新创空间

创建或改设置前先查可用选项，避免写死过期配置：

```bash
curl "https://modelscope.cn/openapi/v1/studios/hardware?sdk_type=${sdk_type}" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl "https://modelscope.cn/openapi/v1/studios/sdk-versions?sdk_type=gradio" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl "https://modelscope.cn/openapi/v1/studios/base-images" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

已有创空间时可给硬件查询追加 `&studio=${owner}/${repo}`，让免费资源按该空间可用额度返回。选择 `hardware` 时使用返回项的 `name`；付费资源格式为 `paid/<InstanceType>`。选择 Gradio `sdk_version` 时使用返回项的 `version`。选择 `base_image` 时使用返回项的 `name`。

**付费资源授权要求：** 如果准备把 `hardware` 设置为 `paid/<InstanceType>` 或返回项 `resource_type=paid`，必须先明确告知用户这会对其 ModelScope 绑定的阿里云账号产生费用，并得到用户明确授权后才能创建、更新设置或重新部署。未获授权时只能选择免费资源。

检查是否已存在：

```bash
curl "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}" -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 等价 CLI： ms info ${owner}/${repo} --repo-type studio
```

**不存在 → 创建**（创建前主动询问用户「公开还是私有？」默认私有）：

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "'"${owner}"'",
    "repo_name": "'"${repo}"'",
    "sdk_type": "gradio",
    "visibility": "private",
    "hardware": "platform/2v-cpu-16g-mem",
    "display_name": "My App"
  }'
# 等价 CLI： ms create ${owner}/${repo} --repo-type studio --sdk-type gradio --private
```

**已存在 → 按需更新设置：**

```bash
curl -X PATCH "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"sdk_type": "gradio", "sdk_version": "6.2.0", "base_image": "ubuntu22.04-py311-torch2.9.1-modelscope1.35.0"}'
# 等价 CLI： ms settings ${owner}/${repo} --repo-type studio sdk_type=gradio sdk_version=6.2.0
```

`sdk_type`、`sdk_version`、`base_image`、`hardware` 修改后需重新部署才能生效。xGPU 需申请（https://modelscope.cn/docs/studios/xGPU）。

### Step 4: 处理敏感信息

推送代码前，扫描文件中的硬编码敏感信息（API Key、Token、密码等），改为环境变量读取：

```python
# ❌ WRONG
api_key = "sk-xxxxxxxxxxxx"
# ✅ CORRECT
import os
api_key = os.environ.get("API_KEY")
```

汇总变量清单，供 Step 6 使用：非敏感配置放明文变量，API Key、Token、密码等敏感信息放密文变量。

### Step 5: 同步代码到创空间 ⚠️ 唯一的非 API 操作

代码同步通过 **Git** 完成，没有对应的 OpenAPI/CLI 端点。默认分支 `master`，禁止 force push。

```bash
# 1. 配置远程仓库（已有 .git 则跳过 init，已有 modelscope remote 则跳过 add）
[ -d .git ] || git init
git remote remove modelscope 2>/dev/null || true
git remote add modelscope https://oauth2:${MODELSCOPE_API_KEY}@www.modelscope.cn/studios/${owner}/${repo}.git

# 2. 大文件处理（超过 100MB 必须用 LFS）
git lfs install

# 3. 拉取远程并合并
git fetch modelscope master
git merge modelscope/master --allow-unrelated-histories -m "Merge remote"
```

合并冲突时保留本地版本：

```bash
git checkout --ours . && git add . && git commit -m "Resolve conflicts, keep local version"
```

提交并推送：

```bash
git add . && git commit -m "Deploy to ModelScope Studio"
git push -u modelscope master
```

### Step 6: 配置明文/密文变量

根据 Step 4 的清单配置（API 优先）。明文变量返回 key 和 value，仅用于非敏感配置：

```bash
# 列出明文变量
curl "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 添加
curl -X POST "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/tmp/gradio"}'
# 更新
curl -X PUT "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/mnt/workspace/tmp"}'
# 删除
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR"}'
```

密文变量不会返回 value，用于 API Key、Token、密码等敏感信息：

```bash
# 列出密文变量（只返回 key）
curl "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 添加
curl -X POST "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "sk-xxx"}'
# 更新
curl -X PUT "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "new-value"}'
# 删除
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"key": "API_KEY"}'
# 等价 CLI（仅密文变量）： ms secret {list,add,update,delete} ${owner}/${repo}
```

> ⚠️ 删除明文/密文变量都用 `DELETE .../variables` 或 `DELETE .../secrets` 并在 **body** 传 `{"key":"..."}`，不是 `DELETE .../{key}` 路径形式。

### Step 7: 部署创空间

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 等价 CLI： ms deploy ${owner}/${repo} --repo-type studio
```

### Step 8: 监控状态和日志

```bash
# 运行日志
curl "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/logs/run" -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 构建日志（Docker 类型）
curl "https://modelscope.cn/openapi/v1/studios/${owner}/${repo}/logs/build" -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 等价 CLI： ms logs ${owner}/${repo} --log-type run|build
```

按 SDK 类型查看日志：

- `docker`：先查 `build`，构建完成后查 `run`
- 其他类型：直接查 `run`

持续交替查看，直到 `Running` 或发现错误。

### Step 9: 自动诊断和修复

**通用错误：**

| 错误特征 | 修复方案 |
|----------|----------|
| `ModuleNotFoundError` | 添加到 requirements.txt |
| `SyntaxError` | 修复代码语法 |
| `MemoryError` | 建议优化内存或升级硬件配置；如需切换到付费资源，先按 Step 3 获取明确授权 |
| `Permission denied` | 检查文件权限 |
| 变量为空 | 检查 Step 6 |

**Docker 特有错误：**

| 错误特征 | 修复方案 |
|----------|----------|
| 端口问题 / `Address already in use` | 确保监听 `0.0.0.0:7860`，不用 8080 |
| `COPY failed` | 检查 Dockerfile 文件路径 |
| `RUN` 步骤失败 | 检查依赖安装命令 |
| 镜像拉取失败 | 检查 FROM 基础镜像地址 |

修复流程：分析日志 → 修改代码 → `git push` → `POST .../deploy`（或 `ms deploy`）→ 再次查日志

### Step 10: 完成部署

提供创空间 URL：`https://modelscope.cn/studios/${owner}/${repo}`

> 如果创空间为私有，提示用户：「部署已成功，当前为私有。是否需要改为公开？」确认后 `PATCH .../settings` 传 `{"visibility": "public"}`（或 `ms settings ${owner}/${repo} --repo-type studio private=false`）。

## Docker 创空间参考

适用于 FastAPI、Golang、Node.js 等超出 Gradio/Streamlit 范畴的应用。
前置：需在魔搭平台完成阿里云账号绑定并通过实名认证，详见 https://modelscope.cn/docs/studios/docker 。详见 `references/docker-templates.md`。

**关键要求：**

- 端口必须暴露 `0.0.0.0:7860`，禁止使用 `8080`（平台占用）
- HTTP Header 禁止使用 `Authorization`、`X-modelscope-*`、`X-studio-*`

## 数据持久化

- 默认每次重启数据丢失
- 持久化目录：`/mnt/workspace`
- 转移/重命名创空间时数据仍会丢失
- 高可靠性需求使用外部存储（OSS、数据库）

## 注意事项

1. 默认分支 `master`，禁止 force push
2. 超过 100MB 文件必须用 Git LFS
3. Docker 类型首次构建约 3-5 分钟，其他类型启动较快
4. 免费配额有时长限制
5. 切换到付费硬件资源会对用户 ModelScope 绑定的阿里云账号产生费用，必须先得到用户明确授权
6. 代码中禁止硬编码敏感信息，必须通过密文变量注入；非敏感配置可用明文变量
7. 创空间**无法通过编程接口删除**：OpenAPI `DELETE /openapi/v1/studios/{id}` 返回 404；SDK/CLI 的 `delete_repo` 已废弃且不支持 studio。删除只能到网页控制台 https://modelscope.cn （其走 cookie 鉴权的内部接口，Bearer token 调用返回 401）。编程侧只能停止（`stop`）。

## 参考文档

遇到问题或需要更多细节时查阅：

- `references/openapi-studio-endpoints.md` — Studios OpenAPI 端点参数详解（事实来源规格）
- `references/docker-templates.md` — Docker 类型 Dockerfile 模板（FastAPI、Node.js、Golang 等）
- `references/troubleshooting.md` — 部署失败排查流程、常见错误及修复方案

<details>
<summary>附录：MCP 工具首次配置（可选）</summary>

#### 查询已有部署链接

```bash
curl -s "https://modelscope.cn/openapi/v1/mcp/servers/maasadmin/studio-mcp?get_operational_url=true" \
  -H "Authorization: Bearer ${MODELSCOPE_API_KEY}"
```

检查返回 JSON 中 `data.operational_urls`，如有 `accessible: true` 的条目则提取 `url`。

#### 部署 MCP 服务（无可用链接时）

```bash
ms mcp deploy maasadmin/studio-mcp --transport-type streamable_http
```

> MCP deploy 的 `transport_type` 为必填，合法值 `sse` / `streamable_http`；详见 ms-hub 的 MCP 章节。

#### 写入本地 MCP 配置（Cursor `.cursor/mcp.json`）

```json
{
  "mcpServers": {
    "modelscope-studio": {
      "type": "streamable_http",
      "url": "<部署URL>",
      "name": "modelscope-studio"
    }
  }
}
```

其他客户端按各自文档添加 Streamable HTTP 类型 MCP 服务，使用同一 URL。配置完成后调用 MCP 工具 `getCurrentUser` 验证连接。

</details>

## 相关 Skill

- Hub 仓库管理 / 模型数据集 / MCP / 技能管理 → ms-hub
