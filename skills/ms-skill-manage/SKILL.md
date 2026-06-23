---
name: ms-skill-manage
description: >-
  在 ModelScope 技能中心搜索、查看、安装、发布和管理 Agent Skills。
  当用户需要查找可用技能、查看技能安装方式、发布自己的技能到技能广场时使用。
  不适用于: Hub 仓库管理（→ ms-hub）、MCP 服务管理（→ ms-mcp-manage）、
  创空间部署（→ ms-studio-deploy）。
---

# ModelScope 技能中心管理

> Verified with modelscope 1.37.1, ModelScope OpenAPI (2026-06-23)

在 ModelScope 技能广场搜索、查看和发布 Agent Skills。通过 OpenAPI 操作。

技能广场地址：https://www.modelscope.cn/skills

## 认证配置

```bash
export MODELSCOPE_API_KEY="your_token"
```

## 快速决策指南

```
用户想要...
│
├── 搜索可用的 AI 技能
│   └── GET /skills?search=...
│
├── 查看技能详情和安装方式
│   └── GET /skills/{id}
│
├── 发布技能到技能中心
│   └── 上传 zip → POST /files/upload → POST /skills
│
├── 更新已发布的技能
│   └── PATCH /skills/{owner}/{skill_name}/settings
│
├── 管理 Hub 仓库
│   └── hand off → ms-hub
│
└── 部署 MCP 服务
    └── hand off → ms-mcp-manage
```

## 核心操作

### 一、搜索技能

```bash
curl "https://modelscope.cn/openapi/v1/skills?search=代码审查&filter.category=developer-tools&page_size=20" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

**搜索参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `search` | string | 关键词搜索（技能名称、描述） |
| `filter.category` | string | 按分类筛选 |
| `filter.developer` | string | 按开发者筛选 |
| `filter.license` | string | 按许可证筛选 |
| `filter.custom_tag` | string | 按自定义标签筛选 |
| `filter.owner` | string | 按所有者筛选 |
| `page_number` | int | 页码，从 1 开始 |
| `page_size` | int | 每页条数，默认 20 |

**技能分类：**

| 分类 ID | 说明 | 数量 |
|---------|------|------|
| `developer-tools` | 开发工具 | 26427 |
| `code-quality-testing` | 代码质量与测试 | 16815 |
| `ai-media` | AI 媒体（图像/视频生成等） | 7203 |
| `frontend-development` | 前端开发 | 6645 |
| `cloud-devops` | 云与运维 | 5157 |
| `marketing-seo` | 营销 SEO | 4991 |
| `skill-management` | 技能管理 | 4032 |
| `other` | 其他 | 1625 |
| `mobile-development` | 移动开发 | 1229 |
| `ai-automation` | AI 自动化 | 1202 |
| `analytics` | 数据分析 | 61 |
| `doc-processing` | 文档处理 | 23 |

> 分类数据来源：`GET /skills?filter.category={id}&page_size=1` 逐项验证（2026-06-23）

**响应结构：**

```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "@author/skill-name",
        "display_name": "技能显示名",
        "description": "技能描述",
        "developer": "开发者",
        "category": "developer-tools",
        "tags": ["category:developer-tools", "custom_tag:api-design"],
        "view_count": 100,
        "downloads": 50,
        "license": "MIT License",
        "source_url": "https://github.com/...",
        "logo_url": "",
        "private": false
      }
    ],
    "total": 80000,
    "page_number": 1,
    "page_size": 20
  }
}
```

### 二、获取技能详情

```bash
curl "https://modelscope.cn/openapi/v1/skills/@ModelScope/modelscope-oauth-skill" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

> 技能 ID 格式为 `@author/skill_name`，其中 `@` 和 `/` 无需 URL 编码。

**详情响应额外包含：**

```json
{
  "data": {
    "id": "@ModelScope/modelscope-oauth-skill",
    "display_name": "ModelScope OAuth Skill",
    "description": "...",
    "install_command": [
      "npx skills add https://modelscope.cn/skills/@ModelScope/modelscope-oauth-skill",
      "curl -fsSL https://modelscope.cn/skills/install.sh | bash -s -- @ModelScope/modelscope-oauth-skill",
      "pip install --upgrade modelscope & modelscope skills add @ModelScope/modelscope-oauth-skill"
    ],
    "locales": {
      "en": {"description": "...", "category": "..."},
      "zh": {"description": "...", "category": "..."}
    }
  }
}
```

### 三、发布技能

发布技能分两步：先上传 zip 文件，再创建技能条目。

#### Step 1: 上传技能文件

```bash
curl -X POST "https://modelscope.cn/openapi/v1/files/upload" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -F "file=@my-skill.zip" \
  -F "type=skill"
```

> zip 包根目录必须且仅可包含 1 个 SKILL.md 文件。

响应返回 `file_id`。

#### Step 2: 创建技能

```bash
curl -X POST "https://modelscope.cn/openapi/v1/skills" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "your-username",
    "skill_name": "my-awesome-skill",
    "display_name": "My Awesome Skill",
    "description": "技能描述",
    "skill_file": "<file_id from step 1>",
    "category": "developer-tools",
    "license": "MIT License",
    "tags": ["api-design", "automation"],
    "source_url": "https://github.com/..."
  }'
```

**注意：**
- `skill_name` 仅允许小写字母、数字和连字符，创建后不可修改
- `owner` 创建后不可修改

### 四、更新技能

```bash
curl -X PATCH "https://modelscope.cn/openapi/v1/skills/your-username/my-awesome-skill/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Updated Skill Name",
    "description": "更新的描述",
    "skill_file": "<new_file_id>",
    "tags": ["new-tag"]
  }'
```

仅传入需要修改的字段，未传的字段保持原值。

## 安装技能

### CLI 安装

```bash
# 安装单个技能（默认到 ~/.agents/skills/）
ms skills add @anthropics/skill-creator

# 安装到指定目录
ms skills add @author/skill-name --local_dir ./my-skills

# 批量安装
ms skills add @author/skill-1 @author/skill-2 --max-workers 8
```

| 参数 | 说明 |
|------|------|
| `skill_ids` | 一个或多个技能 ID（`@author/name`） |
| `--local_dir DIR` | 安装目录（默认 `~/.agents/skills`） |
| `--token TOKEN` | Access Token（私有技能需要） |
| `--max-workers N` | 并发下载数（默认 8） |

> CLI 当前仅支持 `add` 子命令，尚无 `list`/`update`/`remove`。

### SDK 安装

```python
from modelscope.hub.mcp_api import MCPApi
mcp = MCPApi()
local_path = mcp.download_skill(skill_id="@anthropics/skill-creator", local_dir="./my-skills")
```

### 其他安装方式

技能详情中的 `install_command` 还提供：

| 方式 | 命令格式 | 适用场景 |
|------|----------|----------|
| npx | `npx skills add <url>` | Node.js 环境 |
| curl | `curl -fsSL .../install.sh \| bash -s -- <id>` | 通用 Linux/Mac |
| CLI | `ms skills add <id>` | Python 环境 |

## Skill 目录结构要求

```
my-skill/
├── SKILL.md          # 必须，技能定义（YAML frontmatter + Markdown 指令）
├── scripts/          # 可选，工具脚本
├── references/       # 可选，参考文档
└── examples/         # 可选，示例代码
```

SKILL.md 必须包含 YAML frontmatter：

```yaml
---
name: my-skill-name
description: >-
  技能的简要描述。说明什么时候使用、什么时候不使用。
---
```

## 相关 Skill

- Hub 仓库管理 → ms-hub
- 创空间部署 → ms-studio-deploy
- MCP 服务管理 → ms-mcp-manage
