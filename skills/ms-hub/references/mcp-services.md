# MCP 服务发现与配置参考

> ms-hub §8（MCP 服务操作）的展开参考：完整发现→部署→配置 IDE 的编排、IDE 配置模板、SDK↔OpenAPI 字段差异。
>
> MCP 广场：https://www.modelscope.cn/mcp ｜ Verified live 2026-06-29

## CLI / SDK / OpenAPI 对照

| 操作 | CLI | SDK (`MCPApi`) | OpenAPI |
|------|-----|----------------|---------|
| 搜索服务 | `ms mcp list --search "..."` | `list_mcp_servers()` | `PUT /mcp/servers` |
| 服务详情 | `ms mcp info {id}` | `get_mcp_server()` | `GET /mcp/servers/{id}` |
| 我的服务 | — | `list_operational_mcp_servers()` | `GET /mcp/servers/operational` |
| 部署服务 | `ms mcp deploy {id} --transport-type sse` | — | `POST /mcp/servers/{id}/deploy` |
| 卸载服务 | `ms mcp undeploy {id}` | — | `DELETE /mcp/servers/{id}/undeploy` |

SDK 仅支持搜索/详情/已部署列表；部署与卸载用 CLI 或 OpenAPI。

```python
from modelscope.hub.mcp_api import MCPApi
mcp = MCPApi(); mcp.login(access_token="YOUR_TOKEN")
```

## 部署接口的关键约束

`POST /mcp/servers/{id}/deploy` 的 body：

| 字段 | 必填 | 说明 |
|------|------|------|
| `transport_type` | **是** | 合法值 `sse` / `streamable_http`。**缺省会返回 HTTP 400 `invalid transport_type`** |
| `expiration_minutes` | 否 | 有效期（分钟） |
| `auth_check` | 否 | 是否校验鉴权 |
| `env_info` | 否 | `{KEY: value}` 形式的环境变量（部分服务需要 API Key） |

- **部署的 transport 决定返回的唯一 URL**：`sse` → `.../sse`；`streamable_http` → `.../mcp`。operational 列表只返回所部署的那一种，不是两种都给。
- `ms mcp deploy {id}` 之所以可省略，是因为 CLI 默认 `transport_type=sse`；要 streamable 用 `--transport-type streamable_http`。
- **分页上限**：`page_number × page_size ≤ 100`，服务端强制（超出返回 HTTP 403 `QuotaLimitExceed`），与 Hub/Skills 的 3000 不同。

```bash
# OpenAPI 部署（必带 transport_type）
curl -X POST "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" -H "Content-Type: application/json" \
  -d '{"transport_type": "streamable_http"}'
```

## SDK ↔ OpenAPI 字段差异

SDK 内部对 OpenAPI 原始响应做了键名转换：

| OpenAPI 原始 | SDK 转换后 |
|--------------|-----------|
| `data.mcp_server_list` | `data.servers` |
| 条目内 `operational_urls: [{url, transport_type, accessible, ...}]` | `mcp_servers: [{type, url}]` |

搜索响应条目含：`id`, `name`, `chinese_name`, `description`, `categories`, `tags`, `logo_url`, `is_hosted`, `env_schema`。

## 完整编排：为 Agent 配置一个 MCP 工具

```python
from modelscope.hub.mcp_api import MCPApi
import requests

TOKEN = "YOUR_TOKEN"; BASE = "https://modelscope.cn/openapi/v1"
mcp = MCPApi(); mcp.login(access_token=TOKEN)

# 1. 搜索合适的服务
for s in mcp.list_mcp_servers(search="天气")["servers"]:
    print(s["id"], s["description"])

# 2. 查看详情（确认 is_hosted、env_schema 是否需要 API Key）
detail = mcp.get_mcp_server(server_id="选中的服务 ID")

# 3. 部署（transport_type 必填）
requests.post(f"{BASE}/mcp/servers/{detail['id']}/deploy",
              headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
              json={"transport_type": "streamable_http"})

# 4. 从 operational 取连接地址
mcp_url = None
for s in mcp.list_operational_mcp_servers()["servers"]:
    if s["id"] == detail["id"]:
        for ep in s["mcp_servers"]:
            if ep["type"] == "streamable_http":
                mcp_url = ep["url"]

# 5. 把 mcp_url 写入 IDE / Agent 的 MCP 配置（见下方模板）
print("MCP URL:", mcp_url)
```

> 从 operational API 取到的 URL 即为完整 MCP 端点，无需额外拼接。

## IDE / Agent 配置模板

**Cursor**（`.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "服务名称": {
      "type": "streamable_http",
      "url": "<部署URL>",
      "name": "服务名称"
    }
  }
}
```

**Claude Code**（`.mcp.json`）：

```json
{
  "mcpServers": {
    "服务名称": { "type": "streamable_http", "url": "<部署URL>" }
  }
}
```

**VS Code (Copilot)** / **Codex** / 通用 Agent：按各客户端文档添加一个 Streamable HTTP（或 SSE）类型的远程 MCP 服务，URL 用上面取到的同一地址。若客户端只支持 SSE，部署时改用 `transport_type=sse` 并取 `.../sse` 地址。

不确定客户端如何配置时，打印 URL 让用户手动添加。
