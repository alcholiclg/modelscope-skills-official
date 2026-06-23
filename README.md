# ModelScope Skills

ModelScope Skills 为 AI Agent 提供 [ModelScope 魔搭社区](https://modelscope.cn) 的操作能力——模型/数据集管理、创空间部署、MCP 服务配置、技能中心使用。兼容 Cursor、Claude Code、Codex、Gemini CLI 等主流 Coding Agent 工具。

本仓库遵循 [Agent Skills](https://agentskills.io/home) 标准格式。

> [!NOTE]
> 优先安装 [`ms-hub`](skills/ms-hub/SKILL.md) 技能——它是整个 ModelScope 平台的统一操作入口，让 Agent 可以通过 `ms` CLI、Python SDK 和 OpenAPI 完成绝大多数平台操作。

## 可用技能

| 名称 | 说明 | 文档 |
|------|------|------|
| `ms-hub` | 统一操作入口——模型/数据集搜索下载上传、创空间管理、MCP 服务、技能中心 | [SKILL.md](skills/ms-hub/SKILL.md) |
| `ms-studio-deploy` | 将本地项目部署到创空间（Gradio / Streamlit / Docker / 静态站），含完整部署流程和自动诊断 | [SKILL.md](skills/ms-studio-deploy/SKILL.md) |
| `ms-mcp-manage` | 搜索、部署 MCP 服务并配置到 IDE 或 Agent 框架 | [SKILL.md](skills/ms-mcp-manage/SKILL.md) |
| `ms-skill-manage` | 在技能中心搜索、安装和发布 Skills | [SKILL.md](skills/ms-skill-manage/SKILL.md) |

## 安装

### 通过 ModelScope CLI（通用）

```bash
pip install modelscope
ms skills add @ModelScope/ms-hub
```

技能默认安装到 `~/.agents/skills/`，主流 Agent 工具会自动发现。

另外可以选择从源码安装：

```bash
git clone https://github.com/modelscope/modelscope-skills.git
cp -r modelscope-skills/skills/ms-hub ~/.agents/skills/
```

### Cursor

通过 Cursor Marketplace 安装，或将 `skills/` 下的文件夹复制到 `.cursor/skills/`。

### Claude Code

```
/plugin marketplace add modelscope/modelscope-skills
/plugin install ms-hub@modelscope/modelscope-skills
```

### Codex

将文件夹复制或软链接到 `$HOME/.agents/skills`（或 `$REPO_ROOT/.agents/skills`）。

### Gemini CLI

```bash
gemini extensions install https://github.com/modelscope/modelscope-skills.git --consent
```

## 使用

装好之后直接对 Agent 说你想做什么：

- "下载 Qwen2.5-7B-Instruct"
- "把这个项目部署到魔搭创空间"
- "找一个地图 MCP 服务配置到 Cursor"
- "发布我的 Skill 到技能中心"

Agent 会自动加载对应的 Skill 并执行。

## 前置要求

```bash
pip install modelscope
export MODELSCOPE_API_KEY="your_token"  # https://modelscope.cn/my/myaccesstoken
```

## 技能关系

```
ms-hub（统一入口 / 速查）
 ├── ms-studio-deploy（创空间完整部署流程）
 ├── ms-mcp-manage（MCP 服务详细配置）
 └── ms-skill-manage（技能发布流程）
```

`ms-hub` 覆盖常用操作的速查命令；遇到复杂场景时自动 hand off 到专项 Skill。

## 贡献

1. `skills/` 下新建文件夹
2. 编写 `SKILL.md`：
   ```markdown
   ---
   name: my-skill
   description: 技能用途和触发条件
   ---

   # 标题
   指引 + 示例 + 约束
   ```
3. 按需添加脚本、模板、参考文档
4. 提交 PR

## 许可证

Apache License 2.0

## 相关链接

- [ModelScope 官方文档](https://modelscope.cn/docs/)
- [ModelScope 技能中心](https://modelscope.cn/skills)
- [ModelScope MCP 广场](https://modelscope.cn/mcp)
- [Agent Skills 标准](https://agentskills.io/home)
