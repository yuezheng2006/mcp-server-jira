# Personal JIRA MCP

一个基于FastMCP框架的个人JIRA集成插件，用于查询JIRA问题详情、列表及进行基本操作，支持JIRA附件管理。

## 什么是MCP？

MCP (Model Context Protocol) 是一种为大型语言模型(LLM)提供上下文和工具的标准化协议。它被称为"AI的USB-C接口"，提供了统一的方式连接LLM与各种资源和功能。

本项目是一个MCP服务器，专门针对JIRA集成，允许AI通过标准化接口访问JIRA数据和功能，使得人工智能助手能够：
- 查询和检索JIRA问题
- 创建和更新工作项
- 下载和管理附件
- 执行JIRA相关操作

## 主要功能

- 查询JIRA问题详情和问题列表
- 创建和更新JIRA问题
- 获取项目列表和详情
- 管理和下载JIRA问题附件
  - 自动将附件保存到~/.jira_mcp目录
  - 按问题ID组织的子目录结构
  - 支持下载单个或所有附件

## 安装

### 前提条件

- Python 3.10 或更高版本
- 安装 uv (推荐) 或 pip

### 安装 uv

uv 是一个快速的 Python 包管理器，推荐用于安装和管理 Python 包。

#### Linux / macOS
```bash
# 使用 curl 安装
curl -sSf https://astral.sh/uv/install.sh | sh

# 或使用 pip 安装
pip install uv
```

#### Windows
```bash
# 使用 PowerShell 安装
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip 安装
pip install uv
```

#### 验证安装
```bash
uv --version
```

### 从PyPI安装

```bash
# 使用 uv (推荐)
uv pip install personal-jira-mcp

# 或使用 pip
pip install personal-jira-mcp
```

### 从GitHub安装

```bash
# 使用 uv (推荐)
uv pip install git+https://github.com/yuezheng2006/mcp-server-jira.git

# 或使用 pip
pip install git+https://github.com/yuezheng2006/mcp-server-jira.git
```

### 本地开发安装

```bash
# 克隆仓库
git clone https://github.com/yuezheng2006/mcp-server-jira.git
cd mcp-server-jira

# 使用 uv 安装依赖并开发模式安装
uv pip install -e .

# 或使用 pip
pip install -e .
```

## 配置

创建一个`.env`文件，设置以下环境变量：

```
JIRA_SERVER_URL=http://your-jira-instance.com
JIRA_USERNAME=your_username
JIRA_PASSWORD=your_password
# 或者使用API令牌
JIRA_API_TOKEN=your_api_token
```

### Cursor配置

在 `.cursor/mcp.json` 中添加以下配置（推荐使用uvx方式）：

```json
{
  "mcpServers": {
    "personal-jira-mcp": {
      "command": "uvx",
      "args": [
        "--from=personal-jira-mcp",
        "personal-jira-mcp",
        "--transport",
        "stdio"
      ],
      "env": {
        "JIRA_SERVER_URL": "http://your-jira-instance.com",
        "JIRA_USERNAME": "your_username",
        "JIRA_PASSWORD": "your_password"
      }
    }
  }
}
```

如果您已经本地安装了personal-jira-mcp（不推荐），也可以直接使用命令：

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

### 其他MCP客户端配置

如果你使用其他支持MCP协议的客户端或IDE，可以使用以下两种方式配置：

#### 基于命令行方式
```json
{
  "command": "personal-jira-mcp",
  "args": ["--transport", "stdio"],
  "env": {
    "JIRA_SERVER_URL": "http://your-jira-instance.com",
    "JIRA_USERNAME": "your_username",
    "JIRA_PASSWORD": "your_password"
  }
}
```

#### 基于HTTP方式（需要单独运行服务器）
```json
{
  "url": "http://localhost:8000/mcp",
  "headers": {
    "Authorization": "Bearer your_token_if_needed"
  }
}
```

## 快速开始

### 启动MCP服务器

```bash
# 使用stdio传输模式（默认，适合IDE集成）
personal-jira-mcp --transport stdio

# 使用sse传输模式（适合Web集成）
personal-jira-mcp --transport sse

# 使用streamable-http模式（适合HTTP调用）
personal-jira-mcp --transport streamable-http --port 8000
```

### 命令行工具

```bash
# 下载单个附件
personal-jira-extract ERP-161 example.png --output saved_file.png

# 下载问题的所有附件
personal-jira-attachments ERP-161

# 仅列出问题的所有附件，不下载
personal-jira-attachments ERP-161 --list-only

# 输出附件信息到JSON文件
personal-jira-attachments ERP-161 --output attachments.json
```

### 在Cursor中使用

配置好mcp.json后，可以在Cursor中使用以下自然语言命令：

```
查看JIRA问题ERP-161的详情
```

```
下载JIRA问题ERP-161的所有附件
```

```
搜索所有处于"进行中"状态的JIRA问题
```

## 详细文档

更详细的使用指南和API参考，请查看[使用指南](./mcp.md)。

## MCP提供的工具

本MCP服务器提供以下工具：

| 工具名称 | 描述 | 示例 |
|---------|------|------|
| get_issue | 获取JIRA问题详情 | `ERP-123` |
| search_issues | 搜索JIRA问题列表 | `project = ERP AND status = "In Progress"` |
| create_issue | 创建JIRA问题 | 创建一个标题为"修复登录问题"的任务 |
| update_issue | 更新JIRA问题 | 将ERP-123的状态改为"已完成" |
| get_projects | 获取JIRA项目列表 | 列出所有可访问的项目 |
| get_project | 获取项目详情 | 获取ERP项目的详细信息 |
| get_issue_attachments | 获取问题的所有附件 | 列出ERP-123的所有附件 |
| download_all_attachments | 下载问题的所有附件 | 下载ERP-123的全部附件 |
| get_attachment_by_filename | 获取特定附件 | 从ERP-123获取名为"截图.png"的附件 |

## 开发

### 安装开发依赖

```bash
# 使用 uv
uv pip install -e ".[dev]"

# 或使用 pip
pip install -e ".[dev]"
```

## 发布

### 使用自动化脚本发布

```bash
# 使用包含的发布脚本
./scripts/publish.sh
```

### 手动构建并发布到PyPI

```bash
# 确保已安装构建工具
pip install build twine

# 构建包
python -m build

# 上传到PyPI
python -m twine upload dist/*
```

## 许可证

MIT 