# JIRA MCP 使用指南

JIRA MCP 是一个基于FastMCP框架开发的JIRA插件，提供与JIRA交互的工具和功能。

## 功能特性

- 获取JIRA问题详情
- 搜索JIRA问题列表
- 创建和更新JIRA问题
- 获取JIRA项目信息
- 获取和下载JIRA问题附件

## 配置与设置

### 环境变量

需要设置以下环境变量来连接JIRA服务器：

```bash
export JIRA_SERVER_URL=http://your-jira-server
export JIRA_USERNAME=your-username
export JIRA_PASSWORD=your-password  # 或使用JIRA_API_TOKEN
```

### 启动服务

启动MCP服务器:

```bash
# 使用stdio传输模式
uvx --with-editable . jira-mcp --transport stdio

# 使用sse传输模式
uvx --with-editable . jira-mcp --transport sse
```

## 工具使用示例

### 查询问题详情

```python
from jira_mcp.server import get_issue

# 获取问题详情
issue = get_issue("PROJECT-123")
print(issue["summary"])
```

### 获取问题附件

```python
from jira_mcp.server import get_attachment_by_filename
import base64

# 获取附件
result = get_attachment_by_filename("PROJECT-123", "filename.png")

# 保存附件
if "error" not in result:
    content = base64.b64decode(result["content"])
    with open("saved_file.png", "wb") as f:
        f.write(content)
```

### 使用命令行工具下载附件

```bash
# 使用extract_attachment.py脚本下载附件
python extract_attachment.py PROJECT-123 filename.png --output saved_file.png
```

## 附件管理

JIRA MCP工具会自动将下载的附件保存到`~/.jira_mcp/`目录中，并按照问题ID创建子目录。例如，问题`ERP-161`的附件会保存在`~/.jira_mcp/ERP-161/`目录中。

### 下载单个附件

```bash
# 使用extract_attachment.py脚本下载附件
python extract_attachment.py ERP-161 image-2025-05-12-14-57-30-239.png
```

这会将附件自动保存到`~/.jira_mcp/ERP-161/`目录，并返回附件的相关信息。

### 下载问题的所有附件

```bash
# 下载问题的所有附件
python download_all_attachments.py ERP-161

# 仅列出问题的附件而不下载
python download_all_attachments.py ERP-161 --list-only
```

### 在代码中使用

```python
from jira_mcp.server import get_attachment_by_filename, download_all_attachments

# 获取并保存单个附件
result = get_attachment_by_filename("ERP-161", "image.png")
print(f"附件已保存到: {result['local_path']}")

# 下载问题的所有附件
result = download_all_attachments("ERP-161")
print(f"附件已保存到目录: {result['download_dir']}")
```

## 故障排查

1. **问题附件无法获取**
   
   确保问题ID和附件名称正确。可以使用`debug_issue_fields`函数查看问题的所有字段，包括附件信息：
   
   ```python
   from jira_mcp.server import debug_issue_fields
   
   fields = debug_issue_fields("PROJECT-123")
   # 查看附件字段
   attachment_field = next((f for f in fields["fields"] if f["name"] == "attachment"), None)
   print(attachment_field)
   ```

2. **JIRA连接问题**
   
   检查环境变量是否正确设置，以及JIRA服务器是否可访问。

## API参考

### `get_issue(issue_key)`

获取JIRA问题详情。

### `search_issues(jql, max_results=50, start_at=0)`

根据JQL查询JIRA问题列表。

### `get_attachment_by_filename(issue_key, filename)`

根据问题ID和文件名获取附件内容，返回base64编码的内容和元数据。

### `get_issue_attachments(issue_key, download=False)`

获取JIRA问题的所有附件信息，包括ID、文件名、大小、类型、创建时间和下载URL。当`download=True`时，将下载所有附件到本地目录。

### `download_all_attachments(issue_key)`

下载JIRA问题的所有附件到本地`~/.jira_mcp/[issue_key]/`目录。

### `getIssues(issue_key)`

获取JIRA问题及其所有附件的详细信息，包括问题基本数据和附件列表。

### `debug_issue_fields(issue_key)`

获取问题的完整字段列表，用于调试。 