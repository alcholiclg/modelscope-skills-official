# Studios OpenAPI 端点参考

Base URL: `https://modelscope.cn/openapi/v1`

认证: `Authorization: Bearer $MODELSCOPE_API_KEY`

## 创建创空间

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "username",
    "repo_name": "my-app",
    "sdk_type": "gradio",
    "display_name": "My Application",
    "description": "应用描述",
    "private": true,
    "base_image": "registry.cn-beijing.aliyuncs.com/modelscope-repo/modelscope:ubuntu22.04-py310-torch2.1.2-tf2.14.0-1.11.0",
    "sdk_version": "5.0"
  }'
```

### sdk_type 取值

| 值 | 说明 | 入口文件 |
|-----|------|----------|
| `gradio` | Gradio 应用 | `app.py` |
| `streamlit` | Streamlit 应用 | `app.py` |
| `docker` | Docker 容器 | `Dockerfile` |
| `static` | 静态网站 | `index.html` |

## 获取创空间详情

```bash
curl "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 部署/重启创空间

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/deploy" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 停止创空间

```bash
curl -X POST "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/stop" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 获取运行日志

```bash
# 运行日志
curl "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/logs/run" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# 构建日志（Docker 类型）
curl "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/logs/build" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

## 更新设置

```bash
curl -X PATCH "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/settings" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sdk_type": "gradio",
    "private": false
  }'
```

## 环境变量（Secrets）

```bash
# 列出
curl "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# 添加
curl -X POST "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "sk-xxx"}'

# 更新
curl -X PUT "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY", "value": "new-value"}'

# 删除（key 放在 body，不是路径参数）
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/secrets" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "API_KEY"}'
```

> ⚠️ 删除接口为 `DELETE .../secrets` + body `{"key": "..."}`。
> 路径形式 `DELETE .../secrets/{key}` 会返回 404 且不生效。
