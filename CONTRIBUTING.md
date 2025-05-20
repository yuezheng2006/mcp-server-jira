# 贡献指南

感谢你考虑为JIRA MCP项目做出贡献！以下是一些指导方针，帮助你开始。

## 开发环境设置

1. 克隆仓库

```bash
git clone https://github.com/你的用户名/jira_mcp.git
cd jira_mcp
```

2. 创建虚拟环境

```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 或使用conda
conda create -n jira-mcp python=3.10
conda activate jira-mcp
```

3. 安装开发依赖

```bash
# 使用uv
uv pip install -e ".[dev]"

# 或使用pip
pip install -e ".[dev]"
```

## 开发流程

1. 从主分支创建功能分支
2. 进行代码更改
3. 运行测试确保所有内容正常工作
4. 提交更改并推送到你的仓库
5. 创建Pull Request

## 代码规范

我们使用以下工具来保持代码质量：

- black用于代码格式化
- isort用于导入排序
- flake8用于代码检查

运行这些工具：

```bash
black src
isort src
flake8 src
```

## 提交信息规范

请遵循以下提交信息格式：

```
<类型>: <描述>

[可选的详细说明]

[可选的关闭问题引用]
```

类型可以是：
- feat：新功能
- fix：错误修复
- docs：文档更改
- style：不影响代码功能的格式更改
- refactor：既不修复错误也不添加功能的代码更改
- perf：提高性能的代码更改
- test：添加或修复测试

## 发布流程

1. 更新版本号（在src/jira_mcp/__init__.py和pyproject.toml中）
2. 更新CHANGELOG.md
3. 创建发布PR
4. 合并后，创建新的发布标签

## 行为准则

请尊重所有项目贡献者和用户，保持积极和包容的社区氛围。

## 许可证

通过提交代码，你同意你的代码将根据项目的MIT许可证发布。 