---
name: ms-hub
description: >-
  ModelScope 魔搭社区统一操作入口。覆盖模型/数据集搜索下载上传、仓库管理、创空间部署、
  MCP 服务搜索部署配置、技能中心搜索安装发布。当用户提到 ModelScope、魔搭、或任何平台操作时使用此 skill。
  复杂的创空间部署流程使用 ms-studio-deploy；MCP 与技能中心的展开细节见本 skill 的 references。
---

# ModelScope 统一操作入口

> Verified with modelscope 1.37.1, Python 3.12 (2026-06-23)

通过 OpenAPI、CLI 和 SDK 操作 ModelScope 魔搭社区全平台能力，覆盖 Hub（模型/数据集）、创空间（Studio）、MCP 服务、技能中心（Skills）。本 Skill 作为速查入口，复杂操作流程需使用专项 Skill。

## 环境要求

```bash
pip install modelscope
```

`modelscope` 包安装后同时获得 SDK（`modelscope.hub.api.HubApi`）和 CLI（`ms`）。CLI 底层由 `modelscope_hub`（v0.1.2）驱动，提供完整的 Hub / Studio / MCP / Skills 命令行操作。

> `ms` 和 `modelscope` 是同一命令的别名，本文统一使用 `ms`。

## 认证配置

所有操作依赖统一认证：

```bash
# 环境变量
export MODELSCOPE_API_KEY="your_token"

# Token 获取地址
# https://modelscope.cn/my/myaccesstoken
```

| 操作方式 | 认证方法 |
|----------|----------|
| OpenAPI | `Authorization: Bearer $MODELSCOPE_API_KEY` |
| CLI | `ms login --token $MODELSCOPE_API_KEY` |
| SDK | `api.login(access_token=os.environ['MODELSCOPE_API_KEY'])` |

## 基础约定

| 项目 | 值 |
|------|-----|
| **OpenAPI Base URL** | `https://modelscope.cn/openapi/v1` |
| **成功响应** | `{"success": true, "data": {...}, "request_id": "..."}` |
| **错误响应** | `{"success": false, "code": "ERROR_CODE", "message": "..."}` |
| **HTTP 状态码** | `200` 成功 / `401` 未授权 / `404` 不存在 / `500` 服务器错误 |
| **默认分支** | `master`（非 main） |
| **分页限制** | `page_number × page_size ≤ 3000` |

## 快速决策指南

```
用户想要...
│
├─── Hub：模型/数据集 ─────────────────────────────
│   ├── 搜索模型/数据集 → OpenAPI GET /models 或 /datasets
│   ├── 查看详情 → GET /models/{owner}/{repo} 或 SDK model_info()
│   ├── 下载 → CLI: ms download owner/repo
│   ├── 上传 → CLI: ms upload owner/repo ./local
│   ├── 创建仓库 → CLI: ms create owner/repo
│   ├── 浏览文件 → SDK: api.get_model_files()
│   ├── 检查数据集 → uv run scripts/ms_inspect_dataset.py
│   └── 版本管理 → SDK: api.get_model_branches_and_tags()
│
├─── Studio：创空间 ──────────────────────────────
│   ├── 创建创空间 → POST /studios 或 CLI: ms create owner/repo --repo-type studio
│   ├── 部署/重启 → CLI: ms deploy owner/repo --repo-type studio
│   ├── 查看状态 → GET /studios/{owner}/{repo}
│   ├── 查看日志 → CLI: ms logs owner/repo --log-type run
│   ├── 停止 → CLI: ms stop owner/repo --repo-type studio
│   ├── 更新设置 → CLI: ms settings owner/repo key=value --repo-type studio
│   ├── 可用配置 → GET /studios/hardware, /studios/sdk-versions, /studios/base-images
│   ├── 明文变量 → GET/POST/PUT/DELETE /studios/{owner}/{repo}/variables
│   ├── 密文变量 → GET/POST/PUT/DELETE /studios/{owner}/{repo}/secrets（或 ms secret ...）
│   └── 完整部署流程 → 详见 ms-studio-deploy
│
├─── MCP：服务管理 ──────────────────────────────
│   ├── 搜索 MCP 服务 → CLI: ms mcp list --search "..."
│   ├── 查看详情 → CLI: ms mcp info @author/name
│   ├── 部署服务 → CLI: ms mcp deploy @author/name
│   ├── 卸载服务 → CLI: ms mcp undeploy @author/name
│   ├── 我的已部署 → GET /mcp/servers/operational
│   └── IDE 配置 / 完整编排 → 详见 references/mcp-services.md
│
├─── Skills：技能中心 ────────────────────────────
│   ├── 搜索技能 → GET /skills?search=...
│   ├── 查看详情 → GET /skills/{id}
│   ├── 安装技能 → CLI: ms skills add @author/skill-name
│   ├── 发布技能 → POST /files/upload + POST /skills
│   ├── 更新技能 → PATCH /skills/{owner}/{skill_name}/settings
│   └── 分类体系 / 打包规范 / 完整发布 → 详见 references/skills-center.md
│
├─── 用户信息 ───────────────────────────────────
│   └── GET /users/me
│
└─── 不支持 ─────────────────────────────────────
    ├── Pull Request（ModelScope 无 PR 系统）
    └── 删除标签/分支（无 API）
```

## 一、资源搜索

### OpenAPI 方式

**搜索模型：**

```bash
curl "https://modelscope.cn/openapi/v1/models?search=Qwen&sort=downloads&page_size=20" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

**搜索参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `search` | 关键词 | `"Qwen"`, `"文本生成"` |
| `owner` | 作者/组织 | `"Qwen"`, `"ZhipuAI"` |
| `sort` | 排序 | `default`, `downloads`, `likes`, `last_modified` |
| `page_size` | 每页数量（最大 50） | `20` |
| `filter.task` | 任务类型 | `text-generation`, `image-captioning` |
| `filter.library` | 框架 | `pytorch`, `safetensors`, `diffusers` |
| `filter.model_type` | 模型类型 | `qwen3_moe`, `glm4v`, `llama` |
| `filter.license` | 许可证 | `Apache License 2.0`, `MIT License` |

**常用筛选组合：**

```bash
# PyTorch 文本生成模型，按下载量排序
/models?filter.library=pytorch&filter.task=text-generation&sort=downloads

# 特定作者的所有模型
/models?owner=Qwen&sort=last_modified
```

**搜索数据集：**

```bash
curl "https://modelscope.cn/openapi/v1/datasets?search=中文对话&sort=downloads&page_size=10" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

**OpenAPI 响应结构（模型列表）：**

```json
{"data": {"models": [{"id": "Qwen/...", "downloads": N, "likes": N, "license": "...", "tasks": [...]}], "total_count": N}}
```

### SDK 方式

```python
from modelscope.hub.api import HubApi

api = HubApi()

# 搜索模型 → dict{"Models": [...], "TotalCount": N}
result = api.list_models(owner_or_group="Qwen", page_number=1, page_size=20)
for m in result["Models"]:
    print(f"{m['Path']} ({m['Downloads']} downloads)")

# 搜索数据集 → dict{"datasets": [...], "total_count": N}
result = api.list_datasets(owner_or_group="AI-ModelScope", page_number=1, page_size=20)
for d in result["datasets"]:
    print(f"{d['id']} ({d['downloads']} downloads)")
```

> **SDK vs OpenAPI 字段名差异**：SDK `list_models` 返回 PascalCase（`Path`, `Downloads`），OpenAPI `/models` 返回 snake_case（`id`, `downloads`）。`list_datasets` 两边均为 snake_case。

## 二、查看详情

### OpenAPI 方式

```bash
# 模型详情
curl "https://modelscope.cn/openapi/v1/models/Qwen/Qwen2.5-72B-Instruct" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# 数据集详情
curl "https://modelscope.cn/openapi/v1/datasets/AI-ModelScope/alpaca-gpt4-data-zh" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### SDK 方式（信息更完整）

```python
info = api.model_info("Qwen/Qwen2.5-72B-Instruct")
# info.readme_content  - README 全文
# info.tags            - 标签列表
# info.downloads       - 下载量
# info.siblings        - 文件列表（含 rfilename, size, sha）
# info.visibility      - 可见性（1=私有, 5=公开）

info = api.dataset_info("AI-ModelScope/alpaca-gpt4-data-zh")
```

### 获取用户信息

```bash
curl "https://modelscope.cn/openapi/v1/users/me" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 三、仓库管理

### 创建仓库

```bash
# CLI
ms create owner/repo-name
ms create owner/repo-name --visibility private
ms create owner/my-lora --aigc --aigc_type LoRA --base_model_id Qwen/Qwen2.5-7B-Instruct
```

```python
# SDK
api.create_repo(
    repo_id="owner/repo-name",
    repo_type="model",         # "model" 或 "dataset"
    visibility=5,              # 1=私有, 5=公开
    license="Apache License 2.0",
    exist_ok=True
)

# 模型专用
api.create_model(model_id="owner/model-name", visibility=5)

# 数据集专用
api.create_dataset(
    dataset_name="dataset-name",
    namespace="owner",
    visibility=5
)
```

### 检查仓库是否存在

```python
exists = api.repo_exists(repo_id="owner/repo", repo_type="model")
```

### 设置可见性

```python
api.set_repo_visibility(repo_id="owner/repo", repo_type="model", visibility=1)
```

### 删除仓库

```python
# ⚠️ 危险操作：删除不可逆，必须获得用户明确确认
api.delete_repo(repo_id="owner/repo", repo_type="model")
```

## 四、文件操作

### 列出文件

```python
files = api.get_model_files(
    model_id="Qwen/Qwen2.5-7B-Instruct",
    revision="master",
    recursive=True
)
for f in files:
    print(f"  {f['Name']}  大小: {f.get('Size', '未知')}")

# 检查文件是否存在
exists = api.file_exists(repo_id="owner/repo", filename="config.json", revision="master")
```

### 读取文件内容

```bash
# 使用工具脚本
uv run scripts/ms_read_file.py \
    --repo_id "Qwen/Qwen2.5-7B-Instruct" \
    --file_path "config.json" \
    --repo_type model
```

```python
# SDK 手动下载
from modelscope.hub.file_download import model_file_download

local_path = model_file_download(
    model_id="Qwen/Qwen2.5-7B-Instruct",
    file_path="config.json"
)
```

### 下载模型/文件

```bash
# CLI 下载完整模型
ms download Qwen/Qwen2.5-7B-Instruct

# CLI 下载指定文件
ms download Qwen/Qwen2.5-7B-Instruct config.json

# CLI 按模式筛选
ms download Qwen/Qwen2.5-7B-Instruct --include "*.json" --exclude "*.safetensors"
```

```python
# SDK 下载快照
from modelscope import snapshot_download

local_dir = snapshot_download(
    model_id="Qwen/Qwen2.5-7B-Instruct",
    cache_dir="/tmp/models",
    allow_file_pattern=["*.json", "*.md"],    # 只下载匹配文件
    ignore_file_pattern=["*.safetensors"]     # 排除大文件
)

# 数据集单文件下载
from modelscope.hub.file_download import dataset_file_download
local_path = dataset_file_download(dataset_id="owner/dataset", file_path="data/train.jsonl")
```

### 上传文件

```bash
# CLI 上传目录
ms upload owner/repo ./local-dir
```

```python
# SDK 上传单文件
api.upload_file(
    path_or_fileobj="/path/to/file.txt",
    path_in_repo="data/file.txt",
    repo_id="owner/repo",
    repo_type="model",
    commit_message="添加数据文件"
)

# SDK 上传目录
api.upload_folder(
    repo_id="owner/repo",
    folder_path="/path/to/folder",
    commit_message="上传模型文件",
    repo_type="model",
    ignore_patterns=["*.pyc", "__pycache__", ".git"]
)
```

### 删除文件

```python
api.delete_files(
    repo_id="owner/repo",
    repo_type="model",
    delete_patterns=["*.tmp", "old_model/*"],
    revision="master"
)
```

### 多文件原子提交

```python
from modelscope.hub.api import CommitOperationAdd

operations = [
    CommitOperationAdd(path_in_repo="config.json", path_or_fileobj="/local/config.json"),
    CommitOperationAdd(path_in_repo="README.md", path_or_fileobj="/local/README.md"),
]
api.create_commit(
    repo_id="owner/repo", operations=operations,
    commit_message="更新配置和文档", repo_type="model"
)
```

### Notebook / 教程适配

从 HuggingFace、Colab、GitHub 教程迁移到 ModelScope 时，核心是替换资产来源：

1. **模型下载**：将 `hf_hub_download` / HF `snapshot_download` 替换为上方的 `ms download` 或 SDK `snapshot_download`
2. **数据集加载**：将 `datasets.load_dataset("hf_id")` 替换为 `MsDataset.load("ms_id")` 或 `dataset_snapshot_download`
3. **仓库搜索**：用 OpenAPI 或 SDK 搜索 ModelScope 上的等效资源

> 完整适配工作流（资产映射、许可检查、执行验证）参见：`ms skills add VoyagerX/modelscope-notebook-develop`

### 防错对比

```python
# ✅ CORRECT — 显式指定 repo_type 提高可读性
api.upload_folder(repo_id="owner/repo", folder_path="./local", repo_type="model")

# ⚠️ 也能工作（repo_type 默认为 model），但建议显式指定
api.upload_folder(repo_id="owner/repo", folder_path="./local")

# ✅ CORRECT — 使用 model_id 参数
snapshot_download(model_id="Qwen/Qwen2.5-7B-Instruct")

# ⚠️ repo_id 也有效，但 model_id 语义更清晰
snapshot_download(repo_id="Qwen/Qwen2.5-7B-Instruct")
```

## 五、数据集检查

ModelScope 目前可以通过前述 API/SDK/CLI 的组合可以完成数据集探索：

- **元信息**：`api.dataset_info()` 或 OpenAPI `GET /datasets/{id}` → 描述、标签、文件列表
- **文件浏览**：`api.get_dataset_files()` → 列出所有文件及大小
- **内容读取**：`ms_read_file.py --repo_type dataset` → 下载并查看单个文件内容
- **深度检查**：`ms_inspect_dataset.py` → 封装上述能力 + `MsDataset.load`，一步完成 schema 提取和样本预览（需下载数据到本地）

### 使用辅助脚本

通过辅助脚本 `scripts/ms_inspect_dataset.py` 快速了解数据集的文件结构、字段 schema 和样本内容。脚本内部调用 SDK（`HubApi.dataset_info` + `MsDataset.load`）完成操作。

> 下方示例用 `uv run`（零配置）；已安装 modelscope 的环境也可直接 `python scripts/ms_inspect_dataset.py ...`，参见文末「工具脚本」。

```bash
# 完整检查（文件结构 + schema + 样本预览）
uv run scripts/ms_inspect_dataset.py \
    --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" \
    --operation full

# 仅查看文件结构
uv run scripts/ms_inspect_dataset.py \
    --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" \
    --operation overview

# 仅查看 schema
uv run scripts/ms_inspect_dataset.py \
    --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" \
    --operation schema --split train

# 仅预览样本
uv run scripts/ms_inspect_dataset.py \
    --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" \
    --operation samples --num_samples 5
```

## 六、版本控制

### 列出分支和标签

```python
branches, tags = api.get_model_branches_and_tags(model_id="Qwen/Qwen2.5-7B-Instruct")

# 详细信息（含 commit hash、时间等）
details = api.get_model_branches_and_tags_details(model_id="owner/repo")
```

### 验证 Revision

```python
valid = api.get_valid_revision(repo_id="owner/repo", revision="v1.0")
```

### 创建标签

```python
api.create_model_tag(
    model_id="owner/model-name",
    tag_name="v1.0"
)
```

### 查看提交历史

```python
commits = api.list_repo_commits(
    repo_id="owner/repo",
    repo_type="model",
    revision="master",
    page_number=1,
    page_size=20
)
```

### 已知限制

| 操作 | 状态 | 说明 |
|------|------|------|
| 列出分支/标签 | ✅ | `get_model_branches_and_tags()` |
| 创建标签 | ✅ | `create_model_tag()` |
| 删除标签 | ❌ | 无 API |
| 创建分支 | ❌ | 需 `git clone` → `git checkout -b` → `git push` |
| 删除分支 | ❌ | 无 API |
| 合并分支 | ❌ | ModelScope 无 PR 系统 |

## 七、创空间操作（Studio）

> 完整部署流程（含代码同步、诊断修复）→ ms-studio-deploy（**以 OpenAPI 为事实来源**，CLI 为等价别名）
>
> CLI 由 modelscope_hub 驱动，是 OpenAPI 的 1:1 薄包装；API 优先的 Python 入口为 `from modelscope_hub import HubApi`。
> 如果 agent 已配置 studio-mcp 工具，也可使用 MCP 工具（`createStudio`, `deployStudio` 等）。

### 创建创空间

```bash
# CLI
ms create USERNAME/my-app --repo-type studio --sdk-type gradio --private

# OpenAPI
curl -X POST "https://modelscope.cn/openapi/v1/studios" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"owner": "USERNAME", "repo_name": "my-app", "sdk_type": "gradio", "visibility": "private"}'
```

| sdk_type | 适用场景 |
|----------|----------|
| `gradio` | Gradio 应用（入口 app.py） |
| `streamlit` | Streamlit 应用 |
| `docker` | 自定义 Docker（端口必须 7860） |
| `static` | 纯静态网站（已构建） |

### 查询可用配置

```bash
curl "https://modelscope.cn/openapi/v1/studios/hardware?sdk_type=gradio" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl "https://modelscope.cn/openapi/v1/studios/sdk-versions?sdk_type=gradio" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl "https://modelscope.cn/openapi/v1/studios/base-images" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

已有创空间时可给硬件查询追加 `&studio=USERNAME/my-app`。`hardware` 使用返回项的 `name`；付费资源格式为 `paid/<InstanceType>`。Gradio `sdk_version` 使用返回项的 `version`，`base_image` 使用返回项的 `name`。

**付费资源授权要求：** 使用 `paid/<InstanceType>` 或返回项 `resource_type=paid` 会对用户 ModelScope 绑定的阿里云账号产生费用；必须先明确告知并得到用户明确授权，才能创建、更新设置或重新部署。

### 部署/重启

```bash
# CLI
ms deploy USERNAME/my-app --repo-type studio

# OpenAPI
curl -X POST "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 查看状态与日志

```bash
# CLI
ms logs USERNAME/my-app --log-type run
ms logs USERNAME/my-app --log-type build  # Docker 类型

# OpenAPI
curl "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/logs/run" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 停止

```bash
# CLI
ms stop USERNAME/my-app --repo-type studio

# OpenAPI
curl -X POST "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/stop" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 更新设置

```bash
# CLI
ms settings USERNAME/my-app --repo-type studio display_name="新名称" private=false

# OpenAPI
curl -X PATCH "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "新名称", "visibility": "public", "sdk_type": "gradio"}'
```

可更新字段：`display_name`, `description`, `visibility`, `sdk_type`, `sdk_version`, `base_image`, `hardware`, `license`。`private` 已废弃，OpenAPI 优先使用 `visibility`。

### 变量管理

明文变量返回 key 和 value，仅用于非敏感配置：

```bash
curl "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl -X POST "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/tmp/gradio"}'
curl -X PUT "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/mnt/workspace/tmp"}'
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR"}'
```

密文变量只返回 key，不返回 value，用于 API Key、Token、密码等敏感信息：

```bash
# CLI
ms secret list USERNAME/my-app
ms secret add USERNAME/my-app API_KEY sk-xxx
ms secret update USERNAME/my-app API_KEY new-value
ms secret delete USERNAME/my-app API_KEY

# OpenAPI
curl "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
curl -X POST "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "sk-xxx"}'
curl -X PUT "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "new-value"}'
# 删除：key 放 body，不是路径参数（DELETE .../{key} 会 404）
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/USERNAME/my-app/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY"}'
```

### 代码同步

```bash
git remote add modelscope https://oauth2:${MODELSCOPE_API_KEY}@www.modelscope.cn/studios/${owner}/${repo}.git
git push -u modelscope master
```

## 八、MCP 服务操作

> 完整编排、IDE 配置模板、SDK↔OpenAPI 字段差异 → 详见 `references/mcp-services.md`
>
> 分页上限 `page_number × page_size ≤ 100`（服务端强制，超出 HTTP 403）。

### 搜索 MCP 服务

```bash
# CLI
ms mcp list --search "地图" --page-size 20

# OpenAPI
curl -X PUT "https://modelscope.cn/openapi/v1/mcp/servers" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"search": "地图", "page_size": 20}'
```

### 查看服务详情

```bash
# CLI
ms mcp info @amap/amap-maps

# OpenAPI
curl "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 部署与卸载

部署时 **`transport_type` 必填**，合法值 `sse` / `streamable_http`；部署的 transport 决定返回的唯一 URL（`sse`→`.../sse`，`streamable_http`→`.../mcp`）。

```bash
# CLI（默认 sse；另一种用 --transport-type streamable_http）
ms mcp deploy @amap/amap-maps
ms mcp undeploy @amap/amap-maps

# OpenAPI（必须带 transport_type，否则 HTTP 400 invalid transport_type）
curl -X POST "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"transport_type": "streamable_http"}'
curl -X DELETE "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps/undeploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 查看我的已部署服务

```bash
curl "https://modelscope.cn/openapi/v1/mcp/servers/operational" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### SDK 方式

```python
from modelscope.hub.mcp_api import MCPApi

mcp = MCPApi()
mcp.login(access_token="YOUR_TOKEN")

# 搜索 → {"total_count": N, "servers": [{"name", "id", "description"}, ...]}
result = mcp.list_mcp_servers(search="天气", total_count=20)
for s in result["servers"]:
    print(f"{s['id']}: {s['description']}")

# 详情 → {"name", "description", "id", "servers": [{"type", "url"}, ...]}
detail = mcp.get_mcp_server(server_id="@amap/amap-maps")

# 已部署 → {"total_count": N, "servers": [{"name", "id", "mcp_servers": [{"type", "url"}]}, ...]}
operational = mcp.list_operational_mcp_servers()
```

> `modelscope.hub.mcp_api.MCPApi` 仅支持搜索、详情、已部署列表。部署/卸载使用 CLI `ms mcp deploy/undeploy` 或 OpenAPI。

## 九、技能中心操作（Skills）

> 分类体系、打包规范、完整发布/更新/安装 → 详见 `references/skills-center.md`

### 搜索技能

```bash
curl "https://modelscope.cn/openapi/v1/skills?search=代码审查&page_size=20" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 查看技能详情

```bash
curl "https://modelscope.cn/openapi/v1/skills/@ModelScope/modelscope-oauth-skill" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 返回 install_command 数组，含多种安装方式
```

### 安装技能

```bash
# CLI 安装
ms skills add @author/skill-name

# 安装到指定目录
ms skills add @author/skill-name --local_dir ./my-skills

# 批量安装多个技能
ms skills add @author/skill-1 @author/skill-2

# Shell 脚本安装
curl -fsSL https://modelscope.cn/skills/install.sh | bash -s -- @author/skill-name

# 指定 Agent
curl -fsSL https://modelscope.cn/skills/install.sh | bash -s -- @author/skill-name --agent cursor
```

| 参数 | 说明 |
|------|------|
| `skill_ids` | 位置参数，一个或多个技能 ID（格式 `@author/name`） |
| `--local_dir DIR` | 安装目录（默认 `~/.agents/skills`） |
| `--token TOKEN` | Access Token |
| `--max-workers N` | 并发下载数（默认 8） |

### 发布技能（速查）

```bash
# Step 1: 上传 zip 包
curl -X POST "https://modelscope.cn/openapi/v1/files/upload" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -F "file=@my-skill.zip" -F "type=skill"
# → 获取 file_id

# Step 2: 创建技能
curl -X POST "https://modelscope.cn/openapi/v1/skills" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"owner": "username", "skill_name": "my-skill", "display_name": "My Skill", "skill_file": "<file_id>", "category": "developer-tools"}'
```

### 更新技能设置

```bash
curl -X PATCH "https://modelscope.cn/openapi/v1/skills/{owner}/{skill_name}/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "新名称", "description": "更新描述", "skill_file": "<new_file_id>"}'
```

可更新字段：`display_name`, `description`, `skill_file`, `tags`, `source_url`, `category`, `license`。不可修改：`owner`, `skill_name`。

## 缓存管理

```bash
ms scan-cache                              # 查看本地缓存
ms scan-cache --dir ~/.cache/modelscope    # 指定缓存目录
ms clear-cache                             # 清理缓存
```

## 已知限制

| 域 | 限制 | 说明 |
|----|------|------|
| Hub | 无 PR 系统 | 协作通过直接 push 完成 |
| Hub | 无行级预览 API | 需 SDK 本地加载检查 |
| Hub | 分页上限 | `page_number × page_size ≤ 3000`；`/models` 单页 `page_size ≤ 50` |
| Hub | 默认分支 master | 非 main |
| Hub | 标签不可删除 | 只能创建 |
| Studio | Docker 需实名 | 阿里云账号绑定 |
| Studio | 端口固定 7860 | 不可用 8080 |
| Studio | 无编程删除 | OpenAPI `DELETE /studios/{id}` 返回 404；SDK/CLI `delete_repo` 废弃且不支持 studio。删除需网页控制台，编程侧只能 `stop` |
| MCP | 部署 `transport_type` 必填 | 合法 `sse`/`streamable_http`，否则 HTTP 400 |
| MCP | 分页上限 ≤ 100 | `page × size > 100` 返回 HTTP 403 |
| MCP | SDK 无部署/卸载 | 使用 CLI `ms mcp deploy/undeploy` 或 OpenAPI |
| Skills | CLI 仅支持 `add` | 暂无 `list`/`update`/`remove` 子命令 |

## 工具脚本

| 脚本 | 用途 |
|------|------|
| `scripts/ms_read_file.py` | 下载并读取仓库文件内容 |
| `scripts/ms_inspect_dataset.py` | 深度检查数据集结构和内容 |

两种执行方式（任选其一）：

```bash
# 方式一：已安装 modelscope 的环境直接用 python（与「环境要求」一致）
python scripts/ms_inspect_dataset.py --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" --operation full

# 方式二：uv 零配置（脚本含 PEP 723 内联依赖，自动建临时环境）
uv run scripts/ms_inspect_dataset.py --dataset_id "AI-ModelScope/alpaca-gpt4-data-zh" --operation full
```

## 与专项 Skill / references 的关系

| 域 | 在 ms-hub | 展开位置 |
|----|-----------|----------|
| Studio | 速查：创建/部署/停止/日志 | **ms-studio-deploy**（完整部署流程、代码同步、诊断修复，API 优先） |
| MCP | 速查：搜索/详情/部署/卸载/已部署 | `references/mcp-services.md`（IDE 配置模板、完整编排、字段差异） |
| Skills | 速查：搜索/详情/安装/发布/更新 | `references/skills-center.md`（分类体系、打包规范、发布流程） |
