# 基于MCP的JIRA集成插件

一个基于FastMCP框架的JIRA集成插件，用于查询JIRA问题详情、列表及进行基本操作，支持JIRA附件管理。

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

### 从GitHub安装

```bash
# 使用 uv (推荐)
uvx install git+https://github.com/yuezheng2006/mcp-server-jira.git

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

在 `.cursor/mcp.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "jira-mcp": {
      "command": "uvx",
      "args": [
        "install",
        "git+https://github.com/yuezheng2006/mcp-server-jira.git",
        "jira-mcp",
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

## 快速开始

### 启动MCP服务器

```bash
# 使用stdio传输模式
jira-mcp --transport stdio

# 使用sse传输模式
jira-mcp --transport sse
```

### 命令行工具

```bash
# 下载单个附件
jira-extract ERP-161 example.png --output saved_file.png

# 下载问题的所有附件
jira-download ERP-161

# 列出问题的所有附件
jira-attachments ERP-161 --output attachments.json
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

## 开发

### 安装开发依赖

```bash
# 使用 uv
uv pip install -e ".[dev]"

# 或使用 pip
pip install -e ".[dev]"
```

## 许可证

MIT 