# 创空间部署问题排查

## 通用错误

| 错误特征 | 原因 | 修复方案 |
|----------|------|----------|
| `ModuleNotFoundError: No module named 'xxx'` | 缺少依赖 | 添加到 `requirements.txt` |
| `SyntaxError` | Python 语法错误 | 检查并修复代码 |
| `MemoryError` / `OOMKilled` | 内存不足 | 升级硬件配置或优化内存使用 |
| `Permission denied` | 文件权限问题 | `chmod +x` 或检查目录权限 |
| `FileNotFoundError` | 文件路径不对 | 检查文件是否已提交到 Git |
| 环境变量为空/None | 未配置 Secret | 通过 MCP 或 OpenAPI 添加 |
| `ImportError: cannot import name` | 版本不兼容 | 在 requirements.txt 中指定版本 |

## Docker 特有错误

| 错误特征 | 原因 | 修复方案 |
|----------|------|----------|
| `Address already in use` | 端口冲突 | 确保监听 `0.0.0.0:7860` |
| `COPY failed: file not found` | 源文件不存在 | 检查 Dockerfile 中的 COPY 路径 |
| `RUN` 步骤失败 | 依赖安装出错 | 检查 pip/npm 命令和网络 |
| 镜像拉取失败 | FROM 基础镜像不可访问 | 使用国内镜像源 |
| 构建超时 | 依赖太多或镜像太大 | 精简依赖，使用多阶段构建 |
| `exec format error` | 架构不匹配 | 确保使用 amd64 基础镜像 |

## 部署状态

| 状态 | 含义 | 处理 |
|------|------|------|
| `Building` | Docker 正在构建 | 等待，查看 build 日志 |
| `Running` | 运行中 | 正常 |
| `Stopped` | 已停止 | 调用 deployStudio 重启 |
| `Failed` | 启动失败 | 查看 run 日志排查 |
| `Sleeping` | 长时间无访问休眠 | 访问 URL 自动唤醒 |

## Git 推送问题

| 错误 | 修复 |
|------|------|
| `Authentication failed` | 检查 Token 是否正确和过期 |
| `remote rejected` | 检查仓库是否存在、权限是否足够 |
| `LFS objects missing` | `git lfs install && git lfs push --all` |
| 合并冲突 | `git checkout --ours . && git add . && git commit` |

## 排查流程

```
部署失败
│
├── 查看日志类型
│   ├── Docker → 先查 build 日志，再查 run 日志
│   └── 其他 → 直接查 run 日志
│
├── 根据日志定位问题
│   ├── 依赖缺失 → 更新 requirements.txt
│   ├── 端口错误 → 确保 7860
│   ├── 代码错误 → 修复代码
│   └── 环境变量 → 检查 Secrets 配置
│
└── 修复后重新部署
    git add . && git commit -m "fix" && git push modelscope master
    然后调用 deployStudio
```
