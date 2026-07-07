# 技能中心：搜索 / 发布 / 安装参考

> ms-hub §9（技能中心操作）的展开参考：分类体系、发布打包规范、安装方式、目录结构。
>
> 技能广场：https://www.modelscope.cn/skills

## 搜索参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `search` | string | 关键词（技能名称、描述） |
| `filter.category` | string | 按分类筛选 |
| `filter.developer` | string | 按开发者筛选 |
| `filter.license` | string | 按许可证筛选 |
| `filter.custom_tag` | string | 按自定义标签筛选 |
| `filter.owner` | string | 按所有者筛选 |
| `page_number` / `page_size` | int | 分页（`page_number × page_size ≤ 3000`） |

```bash
curl "https://modelscope.cn/openapi/v1/skills?search=代码审查&filter.category=developer-tools&page_size=20" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 技能分类（category ID）

| 分类 ID | 说明 |
|---------|------|
| `developer-tools` | 开发工具 |
| `code-quality-testing` | 代码质量与测试 |
| `ai-media` | AI 媒体（图像/视频生成等） |
| `frontend-development` | 前端开发 |
| `cloud-devops` | 云与运维 |
| `marketing-seo` | 营销 SEO |
| `skill-management` | 技能管理 |
| `mobile-development` | 移动开发 |
| `ai-automation` | AI 自动化 |
| `analytics` | 数据分析 |
| `doc-processing` | 文档处理 |
| `other` | 其他 |

## 响应结构

搜索响应 `data.skills[]` 条目含：`id`(`@author/name`)、`display_name`、`description`、`developer`、`category`、`tags`、`view_count`、`downloads`、`license`、`source_url`、`private`。

详情（`GET /skills/{id}`，id 中 `@`/`/` 无需编码）额外含：

```json
{
  "install_command": [
    "npx skills add https://modelscope.cn/skills/@author/name",
    "curl -fsSL https://modelscope.cn/skills/install.sh | bash -s -- @author/name",
    "modelscope skills add @author/name"
  ],
  "locales": { "en": {"description": "...", "category": "..."}, "zh": {...} }
}
```

## 发布技能（两步）

### Step 1: 上传 zip

```bash
curl -X POST "https://modelscope.cn/openapi/v1/files/upload" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -F "file=@my-skill.zip" -F "type=skill"
# → 响应 {"data": {"id": "<uuid>"}}；取 data.id 作为 skill_file（键名是 id，不是 file_id）
```

> zip 包根目录必须且仅可包含 1 个 `SKILL.md` 文件。
> 经 CLI 发布（`ms create --repo-type skill --skill-file <zip>`）时，SKILL.md frontmatter 须含 `name`/`version`/`description`，zip ≤ 5 MB。

### Step 2: 创建技能

```bash
curl -X POST "https://modelscope.cn/openapi/v1/skills" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "owner": "your-username",
    "skill_name": "my-awesome-skill",
    "display_name": "My Awesome Skill",
    "description": "技能描述",
    "skill_file": "<data.id from step 1>",
    "category": "developer-tools",
    "license": "MIT License",
    "tags": ["api-design", "automation"],
    "source_url": "https://github.com/..."
  }'
```

字段约束：`skill_name` 仅允许小写字母、数字、连字符，创建后不可改；`owner` 创建后不可改。

## 更新技能

```bash
curl -X PATCH "https://modelscope.cn/openapi/v1/skills/{owner}/{skill_name}/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"display_name": "新名称", "description": "更新描述", "skill_file": "<new_file_id>", "tags": ["new-tag"]}'
```

仅传需要修改的字段，未传字段保持原值。可更新：`display_name`、`description`、`skill_file`、`tags`、`source_url`、`category`、`license`。不可改：`owner`、`skill_name`。

## 安装技能

> ⚠️ `skills add` 属 **legacy `modelscope` CLI**；`ms`（modelscope_hub）无 `skills` 子命令。两包都注册 `ms`/`modelscope` 入口，生效者取决于安装顺序——若报「no skills command」，用下方 curl 或 SDK（最可靠）。

```bash
modelscope skills add @author/skill-name                       # 默认装到 ~/.agents/skills/
modelscope skills add @author/skill-name --local_dir ./skills  # 指定目录
modelscope skills add @author/skill-1 @author/skill-2          # 批量
```

`modelscope skills add` 参数：

| 参数 | 说明 |
|------|------|
| `skill_ids` | 一个或多个技能 ID（`@author/name`） |
| `--local_dir DIR` | 安装目录（默认 `~/.agents/skills`） |
| `--token TOKEN` | Access Token（私有技能需要） |
| `--max-workers N` | 并发下载数（默认 8） |

> legacy `modelscope` CLI 的 `skills` 仅 `add` 子命令，无 `list`/`update`/`remove`。

最可靠的安装方式（不受入口冲突影响，来自详情 `install_command`）：

| 方式 | 命令 | 适用 |
|------|------|------|
| curl | `curl -fsSL https://modelscope.cn/skills/install.sh \| bash -s -- <id>` | 通用 Linux/Mac |
| SDK | `MCPApi().download_skill(skill_id="@author/name", local_dir="./skills")`（实测可靠） | Python |
| npx | `npx skills add <url>` | Node.js 环境 |

## Skill 目录结构

```
my-skill/
├── SKILL.md          # 必须，技能定义（YAML frontmatter + Markdown 指令）
├── scripts/          # 可选，工具脚本
├── references/       # 可选，参考文档
└── examples/         # 可选，示例代码
```

SKILL.md frontmatter 必须含 `name` 与 `description`：

```yaml
---
name: my-skill-name
description: >-
  技能的简要描述。说明什么时候使用、什么时候不使用。
---
```
