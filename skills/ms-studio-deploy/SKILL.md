---
name: ms-studio-deploy
description: >-
  将本地项目部署到 ModelScope 创空间 (Studio)。支持 Gradio、Streamlit、Docker、静态网站类型。
  覆盖创建、代码同步、部署、日志监控、环境变量管理、自动诊断修复。
  当用户提到部署到 ModelScope、创空间、魔搭社区、魔搭、Studio 部署、Gradio 部署、Streamlit 部署、
  Docker 部署、FastAPI 部署、静态网站部署，或者想要把本地应用、Web 应用、API 服务发布到云端时使用。
  也适用于用户遇到创空间构建失败、运行错误需要排查日志、想要更新已部署的创空间、管理创空间环境变量等场景。
  不适用于: Hub 仓库管理（→ ms-hub）、模型训练、模型评测等任务。
---

# ModelScope 创空间部署

> Verified with ModelScope OpenAPI, modelscope 1.37.1 (2026-06-23)

将本地项目部署到 ModelScope 创空间，支持 CLI、OpenAPI 和 MCP 工具三种操作方式。

## 快速决策指南

```
用户想要...
│
├── 部署本地项目到创空间
│   └── 按下方「完整部署流程」10 步执行
│
├── 更新已部署的创空间
│   └── 修改代码 → git push → ms deploy owner/repo --repo-type studio
│
├── 查看创空间状态/日志
│   └── ms logs owner/repo --log-type run
│
├── 管理环境变量
│   └── ms secret {list,add,update,delete} owner/repo
│
└── 仓库文件管理
    └── hand off → ms-hub
```

## 前置条件

### 1. MODELSCOPE_API_KEY

整个流程依赖此令牌（CLI 认证、Git 推送、环境变量配置），必须最先确认。

```bash
# 1. 先检查环境变量
echo $MODELSCOPE_API_KEY

# 2. 如果环境变量为空，尝试从 git remote 中提取（可能之前配置过）
git remote -v 2>/dev/null | grep modelscope.cn
```

如果环境变量为空但 git remote 中包含形如 `https://oauth2:<token>@www.modelscope.cn/studios/...` 的地址，从中提取 `<token>` 部分作为 `MODELSCOPE_API_KEY` 使用。

两者都没有时，引导用户：
1. 访问 https://modelscope.cn/my/myaccesstoken 获取令牌
2. `export MODELSCOPE_API_KEY=your_token`

### 2. CLI 环境

```bash
pip install modelscope
ms login --token $MODELSCOPE_API_KEY
```

### 3. Git 环境

创空间代码通过 Git 同步，确保已安装 Git 并配置用户信息。

## 操作优先级

### 方式一：CLI

| 操作 | 命令 |
|------|------|
| 获取用户信息 | `ms whoami` |
| 创建创空间 | `ms create owner/repo --repo-type studio --sdk-type gradio` |
| 获取创空间详情 | `ms info owner/repo --repo-type studio` |
| 部署（启动/重启） | `ms deploy owner/repo --repo-type studio` |
| 停止 | `ms stop owner/repo --repo-type studio` |
| 获取日志 | `ms logs owner/repo --log-type run` |
| 更新设置 | `ms settings owner/repo --repo-type studio key=value` |
| 环境变量 | `ms secret {list,add,update,delete} owner/repo` |

### 方式二：OpenAPI

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取用户信息 | GET | `/openapi/v1/users/me` |
| 创建创空间 | POST | `/openapi/v1/studios` |
| 获取详情 | GET | `/openapi/v1/studios/{owner}/{repo}` |
| 部署 | POST | `/openapi/v1/studios/{owner}/{repo}/deploy` |
| 停止 | POST | `/openapi/v1/studios/{owner}/{repo}/stop` |
| 获取日志 | GET | `/openapi/v1/studios/{owner}/{repo}/logs/run` |
| 更新设置 | PATCH | `/openapi/v1/studios/{owner}/{repo}/settings` |
| 环境变量 | GET/POST/PUT/DELETE | `.../secrets` |

**OpenAPI 创建创空间示例：**

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "username",
    "repo_name": "my-app",
    "sdk_type": "gradio",
    "private": true
  }'
```

### 方式三：MCP 工具（需额外配置）

如果 agent 已配置 `studio-mcp` 服务，也可使用 MCP 工具操作：

| 操作 | MCP 工具 |
|------|----------|
| 获取用户信息 | `getCurrentUser` |
| 创建创空间 | `createStudio` |
| 获取创空间详情 | `getStudio` |
| 部署（启动/重启） | `deployStudio` |
| 停止 | `stopStudio` |
| 获取日志 | `getStudioLogs` |
| 更新设置 | `updateStudioSettings` |
| 环境变量 | `listStudioSecrets` / `addStudioSecret` / `updateStudioSecret` / `deleteStudioSecret` |

<details>
<summary>MCP 服务配置方法</summary>

#### 查询已有部署链接

```bash
curl -s -X GET \
  "https://modelscope.cn/openapi/v1/mcp/servers/maasadmin/studio-mcp?get_operational_url=true" \
  -H "Authorization: Bearer ${MODELSCOPE_API_KEY}" \
  -H "Content-Type: application/json"
```

检查返回 JSON 中 `data.operational_urls`，如有 `accessible: true` 的条目则提取 `url`。

#### 部署 MCP 服务（无可用链接时）

```bash
ms mcp deploy maasadmin/studio-mcp
```

#### 写入本地 MCP 配置

**Cursor**（`.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "modelscope-studio": {
      "type": "streamable_http",
      "url": "<部署URL>",
      "name": "modelscope-studio",
      "headers": {}
    }
  }
}
```

如果是**Qoder**，打印如下信息，等待用户手动添加到MCP设置里面：

```json
{
  "mcpServers": {
    "modelscope-studio": {
      "url": "<从 API 返回的 url>",
    }
  }
}
```

其他客户端，按各客户端文档添加 Streamable HTTP 类型 MCP 服务，使用同一 URL，如果不清楚怎么配置，提示用户手动操作。

配置完成后调用 MCP 工具 `getCurrentUser` 验证连接。

</details>

## 完整部署流程

### Step 1: 检查本地 Git 仓库

```bash
[ -d .git ] && git remote -v 2>/dev/null | grep modelscope.cn/studios
```

- 已有创空间远程地址 → 从 URL 提取 `owner` 和 `repo_name`，跳到 Step 3
- 没有 → 继续 Step 2

### Step 2: 分析项目并获取用户信息

#### 2.1 确定 SDK 类型

| 类型 | 检测条件 | 入口文件 | 备注 |
|------|----------|----------|------|
| `gradio` | `app.py` 导入 gradio | `app.py` | 需设置 `sdk_version`, `base_image` |
| `streamlit` | `app.py` 使用 streamlit | `app.py` | 需设置 `base_image` |
| `docker` | 存在 `Dockerfile` | `Dockerfile` | 端口必须 7860 |
| `static` | 存在 `index.html`（已构建） | `index.html` | 不支持构建步骤 |

选择建议：
- `static` 不支持构建步骤，文件必须已构建
- 需构建的前端项目使用 `docker`
- 不确定时使用 `docker`

> `docker` 类型需先在魔搭平台完成阿里云账号绑定并通过实名认证：https://modelscope.cn/docs/studios/docker ，否则无法构建 Docker 镜像。

#### 2.2 获取用户信息

```bash
ms whoami
# 或 OpenAPI: GET /openapi/v1/users/me
```

`repo_name` 从项目目录名或用户指定获取。

### Step 3: 创建或更新创空间

检查创空间是否已存在：

```bash
ms info owner/repo_name --repo-type studio
# 或 OpenAPI: GET /openapi/v1/studios/{owner}/{repo_name}
```

**不存在 → 创建：**

> 创建前主动询问用户：「创空间设为公开还是私有？」默认 `--private`。

```bash
ms create owner/repo_name --repo-type studio --sdk-type gradio --private
```

```bash
# OpenAPI 方式
curl -X POST "https://modelscope.cn/openapi/v1/studios" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "USERNAME",
    "repo_name": "REPO_NAME",
    "sdk_type": "gradio",
    "private": true,
    "display_name": "My App"
  }'
```

**已存在 → 更新设置（按需）：**

```bash
ms settings owner/repo_name --repo-type studio sdk_type=gradio sdk_version=5.0
```

**硬件配置参考：**
- 免费：`platform/2v-cpu-16g-mem`
- xGPU：需申请（https://modelscope.cn/docs/studios/xGPU）

### Step 4: 处理敏感信息

在推送代码前，扫描文件中的敏感信息（API Key、Token、密码、Secret 等）。

1. 逐文件检查，找出硬编码的敏感信息
2. 将硬编码改为环境变量读取：

```python
# ❌ WRONG
api_key = "sk-xxxxxxxxxxxx"

# ✅ CORRECT
import os
api_key = os.environ.get("API_KEY")
```

3. 汇总环境变量清单，供 Step 6 使用。

### Step 5: 同步代码到创空间

默认分支 `master`，禁止 force push。

```bash
# 1. 初始化并配置远程仓库（已有 .git 则跳过 init，已有 modelscope remote 则跳过 add）
[ -d .git ] || git init
git remote remove modelscope 2>/dev/null || true
git remote add modelscope https://oauth2:${MODELSCOPE_API_KEY}@www.modelscope.cn/studios/${owner}/${repo_name}.git

# 2. 大文件处理（超过 100MB 必须用 LFS）
git lfs install

# 3. 拉取远程
git fetch modelscope master
git merge modelscope/master --allow-unrelated-histories -m "Merge remote"
```

合并冲突时保留本地版本：

```bash
git checkout --ours .
git add .
git commit -m "Resolve conflicts, keep local version"
```

提交并推送：

```bash
git add .
git commit -m "Deploy to ModelScope Studio"
git push -u modelscope master
```

### Step 6: 配置环境变量

根据 Step 4 的清单配置：

```bash
# 1. 查看已配置变量
ms secret list owner/repo_name

# 2. 缺失的向用户询问值后配置
ms secret add owner/repo_name API_KEY sk-xxx
```

### Step 7: 部署创空间

```bash
ms deploy owner/repo_name --repo-type studio
```

```bash
# OpenAPI 方式
curl -X POST "https://modelscope.cn/openapi/v1/studios/${owner}/${repo_name}/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### Step 8: 监控状态和日志

```bash
ms logs owner/repo_name --log-type run
ms logs owner/repo_name --log-type build  # Docker 类型
```

按 SDK 类型查看日志：
- `docker`：先查 `log_type="build"`，构建完成后查 `log_type="run"`
- 其他类型：直接查 `log_type="run"`

持续交替查看，直到 `Running` 或发现错误。

### Step 9: 自动诊断和修复

**通用错误：**

| 错误特征 | 修复方案 |
|----------|----------|
| `ModuleNotFoundError` | 添加到 requirements.txt |
| `SyntaxError` | 修复代码语法 |
| `MemoryError` | 建议升级硬件配置 |
| `Permission denied` | 检查文件权限 |
| 环境变量为空 | 检查 Step 6 |

**Docker 特有错误：**

| 错误特征 | 修复方案 |
|----------|----------|
| 端口问题 / `Address already in use` | 确保监听 `0.0.0.0:7860`，不用 8080 |
| `COPY failed` | 检查 Dockerfile 文件路径 |
| `RUN` 步骤失败 | 检查依赖安装命令 |
| 镜像拉取失败 | 检查 FROM 基础镜像地址 |

修复流程：分析日志 → 修改代码 → 推送 → `ms deploy` → 再次检查日志

### Step 10: 完成部署

提供创空间 URL：`https://modelscope.cn/studios/${owner}/${repo_name}`

> 如果创空间为私有，提示用户：「部署已成功，当前为私有。是否需要改为公开？」，确认后执行 `ms settings owner/repo --repo-type studio private=false`。

## Docker 创空间参考

适用于 FastAPI、Golang、Node.js 等超出 Gradio/Streamlit 范畴的应用。
前置要求：需在魔搭平台完成阿里云账号绑定并通过实名认证，详见：https://modelscope.cn/docs/studios/docker
详见 `references/docker-templates.md`

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
5. 代码中禁止硬编码敏感信息，必须通过环境变量注入

## 参考文档

遇到问题或需要更多细节时查阅：

- `references/docker-templates.md` — Docker 类型创空间的 Dockerfile 模板（FastAPI、Node.js、Golang 等）
- `references/troubleshooting.md` — 部署失败排查流程、常见错误及修复方案
- `references/openapi-studio-endpoints.md` — Studios OpenAPI 端点参数详解

## 相关 Skill

- Hub 仓库管理 → ms-hub
- MCP 服务管理 → ms-mcp-manage
- Skills 管理 → ms-skill-manage
