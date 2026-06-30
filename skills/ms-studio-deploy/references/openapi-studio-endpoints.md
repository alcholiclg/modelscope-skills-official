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
    "visibility": "private",
    "hardware": "platform/2v-cpu-16g-mem",
    "base_image": "ubuntu22.04-py311-torch2.9.1-modelscope1.35.0",
    "sdk_version": "6.2.0"
  }'
```

### sdk_type 取值

| 值 | 说明 | 入口文件 |
|-----|------|----------|
| `gradio` | Gradio 应用 | `app.py` |
| `streamlit` | Streamlit 应用 | `app.py` |
| `docker` | Docker 容器 | `Dockerfile` |
| `static` | 静态网站 | `index.html` |

## 查询可用配置

这些接口用于在创建或更新 Studio 前动态选择配置，避免写死过期值。

```bash
# 硬件配置；sdk_type 可选，已有空间时可追加 studio=owner/repo_name
curl "https://modelscope.cn/openapi/v1/studios/hardware?sdk_type=gradio" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# SDK 版本；目前仅 sdk_type=gradio 返回 Gradio 版本列表
curl "https://modelscope.cn/openapi/v1/studios/sdk-versions?sdk_type=gradio" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# 基础镜像
curl "https://modelscope.cn/openapi/v1/studios/base-images" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"
```

使用返回值时：`hardware` 取硬件项的 `name`（付费资源格式为 `paid/<InstanceType>`），`sdk_version` 取 SDK 版本项的 `version`，`base_image` 取基础镜像项的 `name`。

**付费资源授权要求：** 如果 `hardware` 使用 `paid/<InstanceType>` 或硬件返回项 `resource_type=paid`，会对用户 ModelScope 绑定的阿里云账号产生费用。必须先向用户说明费用风险并得到明确授权，才能创建、更新设置或重新部署。

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
    "visibility": "public",
    "sdk_version": "6.2.0",
    "base_image": "ubuntu22.04-py311-torch2.9.1-modelscope1.35.0",
    "hardware": "platform/2v-cpu-16g-mem"
  }'
```

`sdk_type`、`sdk_version`、`base_image`、`hardware` 修改后需重新部署才能生效。`private` 已废弃，OpenAPI 优先使用 `visibility`：`public`、`protected`、`private`。

## 明文变量（Variables）

明文变量返回 key 和 value，仅用于非敏感配置。敏感信息请使用密文变量。

```bash
# 列出
curl "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY"

# 添加
curl -X POST "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/tmp/gradio"}'

# 更新
curl -X PUT "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR", "value": "/mnt/workspace/tmp"}'

# 删除（key 放在 body，不是路径参数）
curl -X DELETE "https://modelscope.cn/openapi/v1/studios/{owner}/{repo_name}/variables" \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "GRADIO_TEMP_DIR"}'
```

## 密文变量（Secrets）

密文变量列表只返回 key，不返回 value，用于 API Key、Token、密码等敏感信息。

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

> ⚠️ 删除明文/密文变量都用 `DELETE .../variables` 或 `DELETE .../secrets` + body `{"key": "..."}`。
> 路径形式 `DELETE .../{key}` 会返回 404 且不生效。
