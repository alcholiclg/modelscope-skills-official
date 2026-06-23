# MCP OpenAPI 端点完整参考

Base URL: `https://modelscope.cn/openapi/v1`

认证: `Authorization: Bearer $MODELSCOPE_API_KEY`

## 搜索 MCP 服务

```
PUT /mcp/servers
```

**请求体：**

```json
{
  "search": "关键词",
  "filter": {
    "category": "communication",
    "tag": "social-media",
    "is_hosted": true
  },
  "page_number": 1,
  "page_size": 20
}
```

**响应：**

```json
{
  "success": true,
  "data": {
    "servers": [
      {
        "id": "@amap/amap-maps",
        "name": "高德地图",
        "description": "地图搜索、路线规划",
        "category": "life-tools",
        "tags": ["map", "navigation"],
        "is_hosted": true
      }
    ],
    "total_count": 42
  }
}
```

## 获取服务详情

```
GET /mcp/servers/{id}
```

可选参数：`?get_operational_url=true`（获取已部署的 URL）

**响应：**

```json
{
  "success": true,
  "data": {
    "id": "@amap/amap-maps",
    "name": "高德地图",
    "description": "地图搜索、路线规划",
    "servers": [
      {
        "type": "sse",
        "url": "https://mcp.api-inference.modelscope.net/{uuid}/sse"
      },
      {
        "type": "streamable_http",
        "url": "https://mcp.api-inference.modelscope.net/{uuid}/streamable_http"
      }
    ],
    "operational_urls": [
      {
        "url": "https://mcp.api-inference.modelscope.net/{uuid}/streamable_http",
        "type": "streamable_http",
        "accessible": true
      }
    ]
  }
}
```

## 获取已部署的服务

```
GET /mcp/servers/operational
```

需要认证，返回当前用户已部署的 MCP 服务及其可用 URL。

## 部署 MCP 服务

```
POST /mcp/servers/{id}/deploy
```

可选请求体：

```json
{
  "transport_type": "streamable_http"
}
```

## 卸载 MCP 服务

```
DELETE /mcp/servers/{id}/undeploy
```

## 注意事项

1. 搜索使用 `PUT` 方法（非 GET），因为需要传递复杂的过滤条件
2. 部署和卸载仅通过 OpenAPI，SDK 不提供这两个方法
3. 服务 ID 格式通常为 `@author/name`，需要 URL 编码
4. 部署后需等待服务启动，通过 `get_operational_url=true` 检查可用性
