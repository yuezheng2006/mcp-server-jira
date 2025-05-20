# 使用FastMCP快速开发MCP服务器

FastMCP是一个强大的Python库，用于简化Model Context Protocol (MCP)服务器和客户端的构建。本指南将介绍如何使用FastMCP快速开发一个MCP服务器，以JIRA MCP为例。

## 什么是MCP

Model Context Protocol (MCP) 是一种标准化协议，用于为大型语言模型(LLM)提供上下文和工具。它被称为"AI的USB-C接口"，提供了一种统一的方式连接LLM与各种资源。MCP服务器可以：

- 通过 **Resources** 提供数据（类似于GET请求，用于加载信息进入LLM上下文）
- 通过 **Tools** 提供功能（类似于POST请求，用于执行代码或产生副作用）
- 通过 **Prompts** 定义交互模式（可重用的交互模板）

FastMCP提供了一个高级、Pythonic的接口，使得开发者可以轻松地构建MCP服务器，无需关心底层协议细节。

## 快速开始

### 1. 安装FastMCP

```bash
# 使用uv (推荐)
uv add fastmcp

# 或使用pip
pip install fastmcp
```

### 2. 创建一个基本MCP服务器

下面是一个最简单的MCP服务器示例：

```python
from fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("My First MCP Server")

# 定义一个工具
@mcp.tool()
def hello(name: str) -> str:
    """向用户问好"""
    return f"你好，{name}！"

# 启动服务器
if __name__ == "__main__":
    mcp.run()
```

### 3. 运行服务器

可以通过以下方式运行服务器：

```bash
# 直接运行Python脚本
python my_server.py

# 或使用FastMCP CLI
fastmcp run my_server.py

# 开发模式（带MCP检查器）
fastmcp dev my_server.py
```

## JIRA MCP服务器实现

以下是JIRA MCP服务器的实现步骤和关键代码，作为一个更复杂的实例参考。

### 1. 项目结构

```
jira_mcp/
├── src/
│   └── jira_mcp/
│       ├── __init__.py
│       ├── config.py     # 配置管理
│       └── server.py     # MCP服务器实现
├── pyproject.toml        # 项目配置
├── README.md             # 项目文档
└── jira_mcp_cli.py       # 命令行入口
```

### 2. 配置管理 (config.py)

```python
import os
import json
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

@dataclass
class JiraSettings:
    """JIRA连接设置."""
    server_url: str 
    username: str
    password: str = ""
    api_token: str = ""

def load_config(config_path: str = None) -> JiraSettings:
    """加载配置，优先从config文件加载，其次是环境变量."""
    # 配置加载逻辑...
    return JiraSettings(
        server_url=os.environ.get("JIRA_SERVER_URL", ""),
        username=os.environ.get("JIRA_USERNAME", ""),
        password=os.environ.get("JIRA_PASSWORD", ""),
        api_token=os.environ.get("JIRA_API_TOKEN", "")
    )

# 创建JIRA设置实例
jira_settings = load_config()
```

### 3. MCP服务器实现 (server.py)

```python
from jira import JIRA
from fastmcp import FastMCP
from .config import get_jira_auth, jira_settings

# 创建MCP服务器
mcp = FastMCP("JIRA MCP Server")

# JIRA客户端
jira_client = None

def get_jira_client() -> JIRA:
    """获取JIRA客户端实例."""
    global jira_client
    if jira_client is None:
        auth = get_jira_auth()
        jira_client = JIRA(server=jira_settings.server_url, basic_auth=auth)
    return jira_client

# 定义MCP工具
@mcp.tool(description="获取JIRA问题详情")
def get_issue(issue_key: str) -> dict:
    """获取JIRA问题详情."""
    client = get_jira_client()
    issue = client.issue(issue_key)
    return format_issue(issue)  # 格式化函数

@mcp.tool(description="搜索JIRA问题列表")
def search_issues(jql: str, max_results: int = 50, start_at: int = 0) -> dict:
    """使用JQL搜索JIRA问题."""
    client = get_jira_client()
    issues = client.search_issues(jql_str=jql, maxResults=max_results, startAt=start_at)
    return {
        "total": issues.total,
        "issues": [format_issue(issue) for issue in issues]
    }

# 主函数
def main():
    """主函数，启动MCP服务器."""
    # 获取传输模式
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    # 运行MCP服务器
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()
```

### 4. 命令行入口 (jira_mcp_cli.py)

```python
#!/usr/bin/env python3
import os
import argparse
from src.jira_mcp.server import main

def cli_main():
    """命令行入口函数."""
    parser = argparse.ArgumentParser(description="JIRA MCP命令行工具")
    parser.add_argument("--transport", "-t", choices=["sse", "stdio"], default="stdio",
                       help="传输模式，默认stdio")
    parser.add_argument("--config", "-c", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.transport:
        os.environ["MCP_TRANSPORT"] = args.transport
    
    if args.config:
        os.environ["MCP_CONFIG_FILE"] = args.config
    
    # 调用主函数
    main()

if __name__ == "__main__":
    cli_main()
```

### 5. 项目配置 (pyproject.toml)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "jira_mcp"
version = "0.1.0"
description = "JIRA MCP for querying JIRA details and lists"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "jira>=3.8.0",
    "fastmcp>=2.0.0",  # 使用最新的FastMCP 2.0
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
jira-mcp = "jira_mcp.server:main"
```

## 高级功能

FastMCP支持多种高级功能，可根据需要添加到你的MCP服务器：

### 资源（Resources）

资源是客户端可以读取的数据源，用于在不执行代码的情况下加载数据。

```python
@mcp.resource("data://jira/projects")
def get_projects() -> dict:
    """获取所有JIRA项目列表作为资源."""
    client = get_jira_client()
    projects = client.projects()
    return {
        "projects": [
            {"key": project.key, "name": project.name}
            for project in projects
        ]
    }
```

### 资源模板（Resource Templates）

资源模板允许客户端通过参数请求特定的资源。

```python
@mcp.resource_template("data://jira/project/{project_key}")
def get_project_details(project_key: str) -> dict:
    """获取特定项目的详细信息."""
    client = get_jira_client()
    project = client.project(project_key)
    return {
        "key": project.key,
        "name": project.name,
        "description": project.description,
        "lead": project.lead.displayName,
    }
```

### 提示（Prompts）

提示是可重用的消息模板，用于引导LLM。

```python
@mcp.prompt()
def jira_issue_template(issue_key: str) -> str:
    """生成查询JIRA问题的提示模板."""
    return f"请提供JIRA问题 {issue_key} 的详细信息，包括状态、优先级和描述。"
```

### 上下文对象（Context Object）

FastMCP提供了上下文对象，用于访问MCP功能：

```python
@mcp.tool()
async def analyze_issue(issue_key: str, ctx) -> dict:
    """分析JIRA问题并记录进度."""
    await ctx.info(f"开始分析问题 {issue_key}")
    
    client = get_jira_client()
    issue = client.issue(issue_key)
    
    # 报告进度
    await ctx.report_progress(progress=1, total=3)
    
    # 业务逻辑...
    
    return {"result": "分析完成", "issue": issue_key}
```

## 部署选项

FastMCP支持多种部署和集成选项：

### 传输协议

- **STDIO**: 最简单的传输方式，适用于本地开发
- **Streamable HTTP**: 适用于Web部署
- **SSE (Server-Sent Events)**: 支持流式传输

```python
# 使用不同传输选项运行服务器
mcp.run(transport="stdio")
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
mcp.run(transport="sse", host="0.0.0.0", port=9000)
```

### ASGI集成

FastMCP服务器可以集成到现有的ASGI应用中：

```python
from fastapi import FastAPI
from fastmcp import FastMCP

# 创建FastAPI应用
app = FastAPI()

# 创建MCP服务器
mcp = FastMCP("My MCP Server")

# 添加工具...

# 获取ASGI应用实例
http_app = mcp.http_app()

# 挂载到FastAPI应用的特定路径下
app.mount("/mcp", http_app)
```

### FastAPI集成

FastMCP可以自动将FastAPI应用转换为MCP服务器：

```python
from fastapi import FastAPI
from fastmcp import FastMCP

# 创建FastAPI应用
app = FastAPI()

@app.get("/items")
def list_items():
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

# 从FastAPI应用创建MCP服务器
mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run()
```

## 服务器组合

FastMCP支持服务器组合，允许多个服务器组合到一个应用中：

```python
from fastmcp import FastMCP
import asyncio

# 创建子服务器
jira_mcp = FastMCP(name="JiraService")

@jira_mcp.tool()
def get_issue(issue_key: str) -> dict:
    """获取JIRA问题."""
    # 实现...
    return {"issue": issue_key}

# 创建主服务器
main_mcp = FastMCP(name="MainApp")

async def setup():
    # 导入子服务器（静态组合）
    await main_mcp.import_server("jira", jira_mcp)
    
    # 或挂载子服务器（动态组合）
    main_mcp.mount("jira", jira_mcp)

if __name__ == "__main__":
    asyncio.run(setup())
    main_mcp.run()
```

## 测试MCP服务器

FastMCP提供了便捷的测试方法：

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def mcp_server():
    server = FastMCP("TestServer")
    
    @server.tool()
    def get_issue(issue_key: str) -> dict:
        return {"issue": issue_key, "status": "Open"}
        
    return server

async def test_tool_functionality(mcp_server):
    # 直接将服务器传递给Client构造函数进行内存中测试
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_issue", {"issue_key": "JIRA-123"})
        assert result[0].text["issue"] == "JIRA-123"
```

## 在Cursor中集成MCP服务器

要在Cursor中集成MCP服务器，需要在`.cursor/mcp.json`中添加配置：

```json
{
  "mcpServers": {
    "jira-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/your-username/jira_mcp.git",
        "jira-mcp"
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

## 最佳实践

### 组织结构

- 使用模块化结构组织代码
- 对配置管理进行抽象
- 将工具、资源和提示按功能分组

### 错误处理

```python
@mcp.tool()
def safe_get_issue(issue_key: str) -> dict:
    """安全地获取JIRA问题，包含错误处理."""
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        return format_issue(issue)
    except Exception as e:
        # 记录错误并返回友好的错误信息
        logger.error(f"获取问题 {issue_key} 时出错: {str(e)}")
        return {
            "error": True,
            "message": f"无法获取问题 {issue_key}: {str(e)}",
            "issue_key": issue_key
        }
```

### 性能优化

- 使用客户端单例模式
- 实现缓存机制
- 对大型响应使用分页

### 安全考虑

- 使用环境变量或安全存储管理凭据
- 实现适当的访问控制
- 限制敏感操作的访问权限

## 总结

使用FastMCP开发MCP服务器的步骤：

1. 安装FastMCP库
2. 创建FastMCP服务器实例
3. 使用装饰器定义工具、资源和提示
4. 配置运行选项并启动服务器
5. 进行测试和集成

FastMCP简化了MCP服务器的开发，使开发者能够专注于业务逻辑，而不必担心底层协议细节。通过遵循本指南中的最佳实践，你可以快速构建功能强大的MCP服务器，扩展大型语言模型的能力。 