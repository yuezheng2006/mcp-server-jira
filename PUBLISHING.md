# Personal JIRA MCP 发布指南

本文档提供了将 Personal JIRA MCP 发布到 PyPI 和其他途径的详细步骤。

## 发布前准备

1. 确保所有代码更改已提交并合并到主分支
2. 更新版本号（遵循语义化版本控制）
   - 在 `pyproject.toml` 中更新 `version`
   - 在 `src/jira_mcp/__init__.py` 中更新 `__version__`
3. 更新 `CHANGELOG.md` 添加版本更新说明
4. 确保所有测试通过
5. 检查文档是否最新

## 构建和上传到 PyPI

### 前置条件

确保你已经安装了必要的工具：

```bash
pip install build twine
```

### 构建分发包

```bash
# 清理之前的构建
rm -rf dist/ build/ *.egg-info/

# 构建源码包和wheel包
python -m build
```

这将在 `dist/` 目录下创建两个文件：
- `personal-jira-mcp-x.y.z.tar.gz` (源码包)
- `personal_jira_mcp-x.y.z-py3-none-any.whl` (wheel包)

### 检查分发包

```bash
# 验证构建的包
twine check dist/*
```

### 上传到测试PyPI（可选但推荐）

```bash
# 上传到测试PyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ personal-jira-mcp
```

### 上传到正式PyPI

```bash
# 上传到PyPI
twine upload dist/*
```

## GitHub发布

1. 在GitHub上创建一个新的Release
2. 标签名称使用 `v版本号`，例如 `v0.1.0`
3. 从CHANGELOG.md复制该版本的更新说明
4. 将构建的分发包作为二进制附件上传

## 更新Cursor配置示例

向用户提供最新的Cursor配置示例，确保与最新版本兼容：

```json
{
  "mcpServers": {
    "personal-jira-mcp": {
      "command": "personal-jira-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "JIRA_SERVER_URL": "http://your-jira-instance.com",
        "JIRA_USERNAME": "your_username",
        "JIRA_PASSWORD": "your_password"
      }
    }
  }
}
```

## Docker镜像（可选）

如果你计划提供Docker镜像，可以按照以下步骤构建并发布：

```bash
# 构建Docker镜像
docker build -t personal-jira-mcp:latest .

# 标记镜像
docker tag personal-jira-mcp:latest yourusername/personal-jira-mcp:latest
docker tag personal-jira-mcp:latest yourusername/personal-jira-mcp:v0.1.0

# 推送到Docker Hub
docker push yourusername/personal-jira-mcp:latest
docker push yourusername/personal-jira-mcp:v0.1.0
```

## 发布后检查

1. 安装已发布的包并验证其功能
2. 检查文档链接是否正常工作
3. 通知用户新版本已发布

## 发布常见问题

### PyPI上传错误

如果遇到上传错误，可能是因为：
- 版本号已存在：确保每次发布使用新的版本号
- 认证问题：检查您的PyPI凭据是否正确
- 包名冲突：确保包名在PyPI上是唯一的

### 安装问题

如果用户报告安装问题：
- 检查依赖关系是否正确定义
- 确认包结构和导入路径是否正确
- 确保清单文件(`MANIFEST.in`)包含所有必要的非代码文件

## 持续集成/持续部署

为简化发布流程，考虑设置GitHub Actions自动化工作流：
1. 当标签为`v*`的提交被推送时，自动构建和发布
2. 自动更新文档网站
3. 自动运行测试套件确保发布质量 