# Docker 创空间模板

前置要求：需在魔搭平台完成阿里云账号绑定并通过实名认证。
详见：https://modelscope.cn/docs/studios/docker

## Python 应用

```dockerfile
FROM python:3.10
WORKDIR /home/user/app
COPY ./ /home/user/app
RUN pip install -r requirements.txt
EXPOSE 7860
ENTRYPOINT ["python", "-u", "app.py"]
```

## Node.js 应用

```dockerfile
FROM node:18
WORKDIR /home/user/app
COPY ./ /home/user/app
RUN npm install
RUN npm run build
EXPOSE 7860
CMD ["npm", "start"]
```

## FastAPI 应用

```dockerfile
FROM python:3.10
WORKDIR /home/user/app
COPY ./ /home/user/app
RUN pip install -r requirements.txt
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Golang 应用

```dockerfile
FROM golang:1.21 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 7860
CMD ["./server"]
```

## 关键要求

1. **端口必须 7860** — 监听 `0.0.0.0:7860`，禁止使用 `8080`（平台占用）
2. **HTTP Header 限制** — 禁止使用 `Authorization`、`X-modelscope-*`、`X-studio-*`
3. **持久化** — 默认每次重启数据丢失，持久化目录 `/mnt/workspace`
4. **大文件** — 超过 100MB 用 Git LFS
5. **首次构建** — 约 3-5 分钟
