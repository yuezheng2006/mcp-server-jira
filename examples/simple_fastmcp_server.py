#!/usr/bin/env python3
"""
简单的FastMCP服务器示例
展示如何使用FastMCP快速构建MCP服务器
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from fastmcp import FastMCP

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO if os.getenv("LOG_LEVEL") != "DEBUG" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP(
    name="Simple FastMCP Server", 
    description="一个简单的MCP服务器示例，展示FastMCP的基本用法"
)

# 模拟数据库
users_db = [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
    {"id": 2, "name": "李四", "email": "lisi@example.com"},
    {"id": 3, "name": "王五", "email": "wangwu@example.com"}
]

tasks_db = [
    {"id": 1, "title": "完成报告", "assigned_to": 1, "status": "进行中"},
    {"id": 2, "title": "准备演示", "assigned_to": 2, "status": "待处理"},
    {"id": 3, "title": "发送邮件", "assigned_to": 1, "status": "已完成"},
]

#-----------------------------------------------------------------------------
# 工具示例 (Tools)
#-----------------------------------------------------------------------------

@mcp.tool()
def get_user(user_id: int) -> Dict[str, Any]:
    """获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        用户信息
    """
    logger.info(f"获取用户: {user_id}")
    
    for user in users_db:
        if user["id"] == user_id:
            return user
    
    return {"error": "用户不存在", "user_id": user_id}


@mcp.tool()
def list_users() -> Dict[str, Any]:
    """获取所有用户列表

    Returns:
        所有用户列表
    """
    logger.info("获取所有用户列表")
    return {"users": users_db}


@mcp.tool()
def search_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None
) -> Dict[str, Any]:
    """搜索任务
    
    Args:
        status: 任务状态筛选
        assigned_to: 指派用户ID筛选
    
    Returns:
        匹配的任务列表
    """
    logger.info(f"搜索任务: status={status}, assigned_to={assigned_to}")
    
    results = tasks_db.copy()
    
    if status:
        results = [task for task in results if task["status"] == status]
        
    if assigned_to:
        results = [task for task in results if task["assigned_to"] == assigned_to]
    
    return {"tasks": results, "total": len(results)}


@mcp.tool()
def create_task(
    title: str,
    assigned_to: int,
    status: str = "待处理"
) -> Dict[str, Any]:
    """创建新任务
    
    Args:
        title: 任务标题
        assigned_to: 指派给的用户ID
        status: 任务状态，默认为"待处理"
    
    Returns:
        创建的任务信息
    """
    logger.info(f"创建任务: {title}")
    
    # 验证用户存在
    user_exists = any(user["id"] == assigned_to for user in users_db)
    if not user_exists:
        return {"error": "指定的用户不存在", "user_id": assigned_to}
    
    # 生成新ID
    new_id = max(task["id"] for task in tasks_db) + 1
    
    # 创建新任务
    new_task = {
        "id": new_id,
        "title": title,
        "assigned_to": assigned_to,
        "status": status
    }
    
    # 添加到数据库
    tasks_db.append(new_task)
    
    return {"success": True, "task": new_task}

#-----------------------------------------------------------------------------
# 资源示例 (Resources)
#-----------------------------------------------------------------------------

@mcp.resource("data://users")
def users_resource() -> Dict[str, Any]:
    """用户列表资源"""
    return {"users": users_db}


@mcp.resource_template("data://user/{user_id}")
def user_resource(user_id: int) -> Dict[str, Any]:
    """特定用户资源"""
    for user in users_db:
        if user["id"] == user_id:
            return user
    return {"error": "用户不存在"}

#-----------------------------------------------------------------------------
# 提示示例 (Prompts)
#-----------------------------------------------------------------------------

@mcp.prompt()
def task_status_prompt(user_name: str) -> str:
    """生成任务状态查询提示"""
    return f"请帮我查询 {user_name} 的所有任务状态，并按状态进行分类展示。"


@mcp.prompt()
def user_introduction(user_id: int) -> str:
    """生成用户介绍提示"""
    # 查找用户信息
    user = None
    for u in users_db:
        if u["id"] == user_id:
            user = u
            break
    
    if user:
        return f"这是{user['name']}的个人介绍，他/她的联系邮箱是{user['email']}。"
    else:
        return f"未找到ID为{user_id}的用户信息。"

#-----------------------------------------------------------------------------
# 启动服务器
#-----------------------------------------------------------------------------

def main():
    """启动MCP服务器"""
    # 获取传输模式，默认为stdio
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    # 获取端口，默认为8000
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    print(f"启动FastMCP服务器，传输模式: {transport}")
    
    # 启动服务器
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        print(f"不支持的传输模式: {transport}，使用默认的stdio模式")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main() 