# ModelScope Skills

ModelScope Skills equip AI agents with the ability to operate on [ModelScope](https://modelscope.cn) — model/dataset management, Studio deployment, MCP service configuration, and Skills Center operations. Compatible with Cursor, Claude Code, Codex, Gemini CLI, and other major coding agent tools.

This repository follows the [Agent Skills](https://agentskills.io/home) standard format.

> [!NOTE]
> Start by installing [`ms-hub`](skills/ms-hub/SKILL.md) — the unified entry point for the entire ModelScope platform, enabling your agent to perform most platform operations via the `ms` CLI, Python SDK, and OpenAPI.

## Available Skills

| Name | Description | Docs |
|------|-------------|------|
| `ms-hub` | Unified operations hub — model/dataset search/download/upload, repo management, Studio quick-ops, MCP services, Skills Center | [SKILL.md](skills/ms-hub/SKILL.md) |
| `ms-studio-deploy` | Deploy local projects to Studios (Gradio / Streamlit / Docker / static), API-first workflow with auto-diagnosis | [SKILL.md](skills/ms-studio-deploy/SKILL.md) |

> MCP service management and Skills Center publishing are now folded into `ms-hub`: common ops live in SKILL.md §8/§9, with depth in `ms-hub/references/mcp-services.md` and `skills-center.md`.

## Installation

### ModelScope CLI (universal)

```bash
pip install modelscope
ms skills add @ModelScope/ms-hub
```

Skills install to `~/.agents/skills/` by default, where major agent tools auto-discover them.

Alternatively, install from source:

```bash
git clone https://github.com/modelscope/modelscope-skills.git
cp -r modelscope-skills/skills/ms-hub ~/.agents/skills/
```

### Cursor

Copy the skill folders from `skills/` into your project's `.cursor/skills/` directory; Cursor auto-discovers the SKILL.md files there.

### Claude Code

```
/plugin marketplace add modelscope/modelscope-skills
/plugin install ms-hub@modelscope/modelscope-skills
```

### Codex

Copy or symlink skill folders into `$HOME/.agents/skills` (or `$REPO_ROOT/.agents/skills`).

### Gemini CLI

```bash
gemini extensions install https://github.com/modelscope/modelscope-skills.git --consent
```

## Usage

Once installed, just tell your agent what you need:

- "Download Qwen2.5-7B-Instruct"
- "Deploy this project to ModelScope Studios"
- "Find a map MCP service and configure it in Cursor"
- "Publish my Skill to the Skills Center"

The agent automatically loads the relevant Skill and executes.

## Prerequisites

```bash
pip install modelscope
export MODELSCOPE_API_KEY="your_token"  # https://modelscope.cn/my/myaccesstoken
```

## Skill Architecture

```
ms-hub (unified entry / quick reference)
 ├── Hub model/dataset/repo operations
 ├── MCP service search·deploy·configure  → references/mcp-services.md
 ├── Skills Center search·install·publish  → references/skills-center.md
 └── ms-studio-deploy (full Studio deployment workflow, API-first)
```

`ms-hub` covers common operations as quick-reference commands; MCP and Skills Center depth lives in references, while the multi-step Studio deployment is split out into `ms-studio-deploy`.

## Contributing

1. Create a new folder under `skills/`
2. Write `SKILL.md`:
   ```markdown
   ---
   name: my-skill
   description: What it does and when to activate
   ---

   # Title
   Guidance + examples + guardrails
   ```
3. Add scripts, templates, reference docs as needed
4. Submit a PR

## License

Apache License 2.0

## Links

- [ModelScope Documentation](https://modelscope.cn/docs/)
- [ModelScope Skills Center](https://modelscope.cn/skills)
- [ModelScope MCP Plaza](https://modelscope.cn/mcp)
- [Agent Skills Standard](https://agentskills.io/home)
