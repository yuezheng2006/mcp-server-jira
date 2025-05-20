# JIRA MCP

一个基于FastMCP框架的JIRA集成插件，用于查询JIRA问题详情、列表及进行基本操作。

## 功能

- 查询JIRA问题详情
- 搜索JIRA问题列表
- 创建新的JIRA问题
- 更新现有JIRA问题
- 获取项目列表和详情

## 安装

### 前提条件

- Python 3.10 或更高版本
- 安装 uv (推荐) 或 pip

### 方法一：从GitHub安装

```bash
# 使用 uv (推荐)
uvx install git+https://github.com/你的用户名/jira_mcp.git

# 或使用 pip
pip install git+https://github.com/你的用户名/jira_mcp.git
```

### 方法二：本地开发安装

```bash
# 克隆仓库
git clone https://github.com/你的用户名/jira_mcp.git
cd jira_mcp

# 使用 uv 安装依赖并开发模式安装
uv pip install -e .

# 或使用 pip
pip install -e .
```

## 配置

### 环境变量

JIRA MCP 需要以下环境变量：

```
JIRA_SERVER_URL=http://your-jira-instance.com
JIRA_USERNAME=your_username
JIRA_PASSWORD=your_password
# 或者使用API令牌
JIRA_API_TOKEN=your_api_token
```

### Cursor配置

在 `.cursor/mcp.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "jira-mcp": {
      "command": "uvx",
      "args": [
        "-m",
        "jira_mcp.server"
      ],
      "transportType": "stdio",
      "env": {
        "JIRA_SERVER_URL": "http://your-jira-instance.com",
        "JIRA_USERNAME": "your_username",
        "JIRA_PASSWORD": "your_password"
      }
    }
  }
}
```

## 使用方法

安装并配置好后，在Cursor中可以使用以下格式的命令：

### 获取问题详情

```
查看JIRA问题PROJ-123的详情
```

### 搜索问题

```
搜索所有状态为"进行中"的JIRA问题
```

### 创建问题

```
在JIRA项目PROJ中创建一个标题为"修复登录BUG"的任务
```

## 开发

### 安装开发依赖

```bash
# 使用 uv
uv pip install -e ".[dev]"

# 或使用 pip
pip install -e ".[dev]"
```

### 代码格式化

```bash
black src
isort src
```

## 贡献

欢迎提交Pull Requests和Issues！

## 许可证

MIT 