---
name: ms-mcp-manage
description: >-
  在 ModelScope MCP 广场搜索、查看、部署和卸载 MCP 服务，并将服务配置到应用中（如 IDE、Agent 框架等）。
  当用户需要查找 MCP 工具、为 Agent 配置 MCP 服务、管理已部署的 MCP 实例时使用。
  不适用于: 创空间部署（→ ms-studio-deploy）、Hub 仓库管理（→ ms-hub）、Skill 管理
  （→ ms-skill-manage）、模型训练/评测。
---

# MCP 服务管理

> Verified with modelscope 1.37.1, Python 3.12 (2026-06-23)

在 ModelScope MCP 广场搜索、部署和管理 MCP 服务。通过 OpenAPI 和 SDK 两种方式操作。

MCP 广场地址：https://www.modelscope.cn/mcp

## 认证配置

```bash
# 环境变量
export MODELSCOPE_API_KEY="your_token"

# Token 获取地址
# https://modelscope.cn/my/myaccesstoken
```

## 快速决策指南

```
用户想要...
│
├── 找一个 MCP 工具
│   └── 搜索服务 → 查看详情 → 部署 → 获取 URL → 配置到 IDE
│
├── 查看已部署的 MCP 服务
│   └── GET /mcp/servers/operational
│
├── 部署一个 MCP 服务
│   └── POST /mcp/servers/{id}/deploy
│
├── 卸载 MCP 服务
│   └── DELETE /mcp/servers/{id}/undeploy
│
├── 在创空间上部署应用
│   └── hand off → ms-studio-deploy
│
└── 管理 Hub 仓库
    └── hand off → ms-hub
```

## 核心操作

> **注意**：OpenAPI 原始响应与 SDK 返回值的键名不同。SDK 内部做了格式转换。
> 本文档 **以 SDK 格式为主展示**，OpenAPI curl 示例中标注原始响应差异。

### 一、搜索 MCP 服务

#### OpenAPI 方式

```bash
curl -X PUT "https://modelscope.cn/openapi/v1/mcp/servers" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "地图",
    "filter": {},
    "page_number": 1,
    "page_size": 20
  }'
# 原始响应: data.mcp_server_list（SDK 转换为 data.servers）
# 原始响应条目含: id, name, chinese_name, description, categories(list), tags, logo_url
```

**过滤参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `search` | string | 搜索关键词（名称、描述、作者） |
| `filter.category` | string | 服务类别（搜索过滤用） |
| `filter.is_hosted` | bool | 是否为托管服务（搜索过滤用） |
| `page_size` | int | 返回数量（最大 100） |

#### SDK 方式

```python
from modelscope.hub.mcp_api import MCPApi

mcp = MCPApi()
mcp.login(access_token="YOUR_TOKEN")

result = mcp.list_mcp_servers(
    search="地图",
    filter={"category": "communication", "is_hosted": True},
    total_count=20
)

for server in result["servers"]:
    print(f"  {server['name']} ({server['id']})")
    print(f"    {server['description']}")
```

### 二、获取服务详情

#### OpenAPI 方式

```bash
curl "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

#### SDK 方式

```python
detail = mcp.get_mcp_server(server_id="@amap/amap-maps")

print(f"名称: {detail['name']}")
print(f"描述: {detail['description']}")
for server in detail["servers"]:
    print(f"  类型: {server['type']}")   # 'sse' 或 'streamable_http'
    print(f"  URL: {server['url']}")
```

**返回结构示例：**

```json
{
  "name": "高德地图",
  "description": "提供地图搜索、路线规划等能力",
  "id": "@amap/amap-maps",
  "servers": [
    {"type": "sse", "url": "https://mcp.api-inference.modelscope.net/{uuid}/sse"},
    {"type": "streamable_http", "url": "https://mcp.api-inference.modelscope.net/{uuid}/streamable_http"}
  ]
}
```

### 三、查看已部署的服务

#### OpenAPI 方式

```bash
curl "https://modelscope.cn/openapi/v1/mcp/servers/operational" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
# 原始响应: data.mcp_server_list（SDK 转换为 data.servers）
# 原始条目含 operational_urls（SDK 转换为 mcp_servers: [{type, url}]）
```

#### SDK 方式

```python
result = mcp.list_operational_mcp_servers()

for server in result["servers"]:
    print(f"  {server['name']} ({server['id']})")
    for endpoint in server["mcp_servers"]:
        print(f"    {endpoint['type']}: {endpoint['url']}")
```

### 四、部署 MCP 服务

```bash
# CLI
ms mcp deploy @amap/amap-maps

# OpenAPI
curl -X POST "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

### 五、卸载 MCP 服务

```bash
# CLI
ms mcp undeploy @amap/amap-maps

# OpenAPI
curl -X DELETE "https://modelscope.cn/openapi/v1/mcp/servers/@amap/amap-maps/undeploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 完整使用流程

### 场景：为 Agent 配置一个 MCP 工具

```python
from modelscope.hub.mcp_api import MCPApi
import requests

TOKEN = "YOUR_TOKEN"
mcp = MCPApi()
mcp.login(access_token=TOKEN)

# 1. 搜索合适的服务
result = mcp.list_mcp_servers(search="天气")
for s in result["servers"]:
    print(f"{s['id']}: {s['description']}")

# 2. 查看详情
detail = mcp.get_mcp_server(server_id="选中的服务 ID")

# 3. 部署服务
requests.post(
    f"https://modelscope.cn/openapi/v1/mcp/servers/{detail['id']}/deploy",
    headers={"Authorization": f"Bearer {TOKEN}"}
)

# 4. 获取连接地址
operational = mcp.list_operational_mcp_servers()
for s in operational["servers"]:
    if s["id"] == detail["id"]:
        for ep in s["mcp_servers"]:
            if ep["type"] == "streamable_http":
                mcp_url = ep["url"]
                break

# 5. 配置到 IDE
print(f"MCP URL: {mcp_url}")
```

## 配置到 IDE / Agent

部署成功后，从 operational API 获取到的完整 URL 即为 MCP 服务端点（`streamable_http` 类型）。
将该 URL 配置到你所使用的 IDE 或 Agent 框架的 MCP 设置中即可，无需额外拼接。

## CLI / SDK / OpenAPI 对照

| 操作 | CLI | SDK (MCPApi) | OpenAPI |
|------|-----|-------------|---------|
| 搜索服务 | `ms mcp list --search "..."` | `list_mcp_servers()` | `PUT /mcp/servers` |
| 服务详情 | `ms mcp info {id}` | `get_mcp_server()` | `GET /mcp/servers/{id}` |
| 我的服务 | — | `list_operational_mcp_servers()` | `GET /mcp/servers/operational` |
| 部署服务 | `ms mcp deploy {id}` | — | `POST /mcp/servers/{id}/deploy` |
| 卸载服务 | `ms mcp undeploy {id}` | — | `DELETE /mcp/servers/{id}/undeploy` |

## 参考文档

- `references/mcp-api-reference.md` — MCP OpenAPI 端点完整参考

## 相关 Skill

- 创空间部署 → ms-studio-deploy
- Hub 仓库管理 → ms-hub
- Skill 管理 → ms-skill-manage
