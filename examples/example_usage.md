# JIRA MCP 使用示例

本文档提供了JIRA MCP的详细使用示例，展示如何使用各种功能与JIRA进行交互。

## 基础用法

以下是在Cursor中使用JIRA MCP的一些基本命令示例：

### 查询问题详情

```
查看JIRA问题KEY-123的详情
```

返回示例：
```json
{
  "id": "10001",
  "key": "KEY-123",
  "summary": "实现用户登录功能",
  "description": "实现基于OAuth的用户登录系统",
  "status": {
    "name": "进行中",
    "id": "3"
  },
  "assignee": {
    "name": "johndoe",
    "display_name": "John Doe"
  }
}
```

### 搜索问题

```
搜索所有由我负责的未解决JIRA问题
```

或使用特定JQL：
```
搜索JIRA问题，JQL: project = PROJ AND status = "In Progress" AND assignee = currentUser() ORDER BY priority DESC
```

### 创建问题

```
在JIRA项目PROJ中创建一个标题为"修复登录页面样式问题"的任务，描述为"登录按钮在移动设备上显示不正确"
```

### 更新问题

```
更新JIRA问题KEY-123，将状态改为"已完成"
```

```
更新JIRA问题KEY-123，添加标签"前端"和"样式修复"
```

## 高级使用

### 使用特定字段查询

```
查找JIRA问题中包含自定义字段"customer"值为"ACME公司"的所有问题
```

### 批量操作

```
将所有"测试中"状态的JIRA问题移动到"已完成"状态
```

## 编程接口示例

如果你想在自己的Python程序中使用JIRA MCP，可以这样做：

```python
import jira_mcp.server as jira_server

# 获取问题详情
issue = jira_server.get_issue("PROJ-123")
print(f"问题标题: {issue['summary']}")

# 搜索问题
issues = jira_server.search_issues("project = PROJ AND status = 'Open'")
print(f"找到 {issues['total']} 个问题")

# 创建问题
new_issue = jira_server.create_issue(
    project_key="PROJ",
    summary="新功能请求",
    description="实现账户设置页面",
    issue_type="Story",
    priority="Medium"
)
print(f"创建了新问题: {new_issue['key']}")
```

## 常见问题排查

### 认证问题

如果遇到"用户名或密码错误"的消息，请确保你已正确设置环境变量：
```
JIRA_SERVER_URL=http://your-jira-instance.com
JIRA_USERNAME=your_username
JIRA_PASSWORD=your_password
```

### 权限问题

如果收到"没有权限执行此操作"的消息，请确保你的JIRA账户有相应的权限。 