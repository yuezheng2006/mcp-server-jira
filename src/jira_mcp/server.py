#!/usr/bin/env python3
import argparse
import logging
import os
import base64
import pathlib
from typing import Dict, List, Any, Optional

from jira import JIRA
from mcp.server.fastmcp import FastMCP
from .config import get_jira_auth, jira_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP("JIRA MCP Server", port=int(os.getenv("MCP_SERVER_PORT", "8000")))

# JIRA客户端
jira_client = None

# JIRA附件保存目录
ATTACHMENTS_DIR = os.path.expanduser("~/.jira_mcp")
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


def get_attachment_path(issue_key: str, filename: str) -> str:
    """获取附件在本地文件系统中的保存路径."""
    # 创建问题专属目录
    issue_dir = os.path.join(ATTACHMENTS_DIR, issue_key)
    os.makedirs(issue_dir, exist_ok=True)
    return os.path.join(issue_dir, filename)


def get_jira_client() -> JIRA:
    """获取JIRA客户端实例."""
    global jira_client
    if jira_client is None:
        auth = get_jira_auth()
        jira_client = JIRA(server=jira_settings.server_url, basic_auth=auth)
    return jira_client


def format_issue(issue) -> Dict[str, Any]:
    """格式化JIRA问题为JSON友好格式."""
    fields = issue.fields
    
    result = {
        "id": issue.id,
        "key": issue.key,
        "self": issue.self,
        "summary": fields.summary,
        "description": fields.description or "",
        "status": {
            "id": fields.status.id,
            "name": fields.status.name,
            "description": fields.status.description,
        },
        "project": {
            "id": fields.project.id,
            "key": fields.project.key,
            "name": fields.project.name,
        },
        "created": fields.created,
        "updated": fields.updated,
    }
    
    # 添加可选字段
    if hasattr(fields, "assignee") and fields.assignee:
        result["assignee"] = {
            "name": fields.assignee.name,
            "display_name": fields.assignee.displayName,
            "email": getattr(fields.assignee, "emailAddress", ""),
        }
    
    if hasattr(fields, "reporter") and fields.reporter:
        result["reporter"] = {
            "name": fields.reporter.name,
            "display_name": fields.reporter.displayName,
            "email": getattr(fields.reporter, "emailAddress", ""),
        }
    
    if hasattr(fields, "issuetype") and fields.issuetype:
        result["issue_type"] = {
            "id": fields.issuetype.id,
            "name": fields.issuetype.name,
            "description": fields.issuetype.description,
        }
    
    if hasattr(fields, "priority") and fields.priority:
        result["priority"] = {
            "id": fields.priority.id,
            "name": fields.priority.name,
        }
    
    if hasattr(fields, "components") and fields.components:
        result["components"] = [
            {"id": c.id, "name": c.name} for c in fields.components
        ]
    
    if hasattr(fields, "labels") and fields.labels:
        result["labels"] = fields.labels
    
    # 处理附件 - JIRA API 使用 "attachment" 字段
    if hasattr(fields, "attachment") and fields.attachment:
        result["attachments"] = [
            {
                "id": attachment.id,
                "filename": attachment.filename,
                "size": attachment.size,
                "content_type": attachment.mimeType,
                "created": attachment.created,
                "url": attachment.content
            }
            for attachment in fields.attachment
        ]
    
    # 获取自定义字段
    for field_name in dir(fields):
        if field_name.startswith("customfield_"):
            value = getattr(fields, field_name)
            if value is not None:
                result[field_name] = value
    
    return result


@mcp.tool(
    description="获取JIRA问题详情",
)
def get_issue(
    issue_key: str,
) -> Dict[str, Any]:
    """获取JIRA问题详情.
    
    Args:
        issue_key: JIRA问题键
    
    Returns:
        Dict[str, Any]: 问题详情
    """
    logger.info(f"获取问题: {issue_key}")
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        return format_issue(issue)
    except Exception as e:
        logger.error(f"获取问题 {issue_key} 失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="获取JIRA问题附件",
)
def get_issue_attachment(
    issue_key: str,
    attachment_id: str,
) -> Dict[str, Any]:
    """获取JIRA问题附件内容.
    
    Args:
        issue_key: JIRA问题键
        attachment_id: 附件ID
    
    Returns:
        Dict[str, Any]: 附件内容
    """
    logger.info(f"获取问题附件: issue={issue_key}, attachment_id={attachment_id}")
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        
        # 查找指定ID的附件
        attachment = None
        
        # 检查attachments字段
        attachments = []
        if hasattr(issue.fields, "attachments") and issue.fields.attachments:
            attachments = issue.fields.attachments
        elif hasattr(issue.fields, "attachment") and issue.fields.attachment:
            attachments = issue.fields.attachment
            
        for att in attachments:
            if att.id == attachment_id:
                attachment = att
                break
        
        if not attachment:
            return {"error": f"未找到ID为 {attachment_id} 的附件"}
        
        # 获取附件内容
        content = attachment.get()
        
        # 确定返回类型：对于图片类型，返回Base64编码；对于文本类型，返回文本内容
        mime_type = attachment.mimeType
        filename = attachment.filename
        
        result = {
            "id": attachment.id,
            "filename": filename,
            "size": attachment.size,
            "content_type": mime_type,
            "created": attachment.created,
        }
        
        # 处理不同的内容类型
        if mime_type.startswith("image/"):
            # 对于图片，返回Base64编码
            result["content"] = base64.b64encode(content).decode('utf-8')
            result["encoding"] = "base64"
        elif mime_type.startswith("text/"):
            # 对于文本文件，直接返回文本内容
            try:
                result["content"] = content.decode('utf-8')
                result["encoding"] = "text"
            except UnicodeDecodeError:
                # 如果解码失败，回退到Base64
                result["content"] = base64.b64encode(content).decode('utf-8')
                result["encoding"] = "base64"
        else:
            # 对于其他类型，返回Base64编码
            result["content"] = base64.b64encode(content).decode('utf-8')
            result["encoding"] = "base64"
        
        return result
    except Exception as e:
        logger.error(f"获取问题 {issue_key} 的附件 {attachment_id} 失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="搜索JIRA问题列表",
)
def search_issues(
    jql: str,
    max_results: int = 50,
    start_at: int = 0
) -> Dict[str, Any]:
    """搜索JIRA问题.
    
    Args:
        jql: JQL查询字符串
        max_results: 最大返回结果数
        start_at: 起始索引
    
    Returns:
        Dict[str, Any]: 搜索结果
    """
    logger.info(f"搜索问题: JQL={jql}, max_results={max_results}, start_at={start_at}")
    try:
        client = get_jira_client()
        issues = client.search_issues(jql_str=jql, maxResults=max_results, startAt=start_at)
        
        return {
            "total": issues.total,
            "issues": [format_issue(issue) for issue in issues],
            "start_at": start_at,
            "max_results": max_results,
        }
    except Exception as e:
        logger.error(f"搜索问题失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="创建JIRA问题",
)
def create_issue(
    project_key: str,
    summary: str,
    description: str = "",
    issue_type: str = "Task",
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """创建JIRA问题.
    
    Args:
        project_key: 项目键
        summary: 问题概要
        description: 问题描述
        issue_type: 问题类型
        priority: 优先级
        assignee: 经办人
        labels: 标签列表
    
    Returns:
        Dict[str, Any]: 创建的问题详情
    """
    logger.info(f"创建问题: project={project_key}, summary={summary}")
    
    try:
        # 构建问题字段
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        
        if description:
            fields["description"] = description
            
        if priority:
            fields["priority"] = {"name": priority}
            
        if assignee:
            fields["assignee"] = {"name": assignee}
            
        if labels:
            fields["labels"] = labels
        
        # 创建问题
        client = get_jira_client()
        issue = client.create_issue(fields=fields)
        return format_issue(issue)
    except Exception as e:
        logger.error(f"创建问题失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="更新JIRA问题",
)
def update_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    issue_type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """更新JIRA问题.
    
    Args:
        issue_key: 问题键
        summary: 问题概要
        description: 问题描述
        issue_type: 问题类型
        priority: 优先级
        assignee: 经办人
        labels: 标签列表
    
    Returns:
        Dict[str, Any]: 更新后的问题详情
    """
    logger.info(f"更新问题 {issue_key}")
    
    try:
        # 构建更新字段
        fields = {}
        
        if summary:
            fields["summary"] = summary
            
        if description:
            fields["description"] = description
            
        if issue_type:
            fields["issuetype"] = {"name": issue_type}
            
        if priority:
            fields["priority"] = {"name": priority}
            
        if assignee:
            fields["assignee"] = {"name": assignee}
            
        if labels:
            fields["labels"] = labels
        
        if not fields:
            return {"error": "未提供任何更新字段"}
        
        # 更新问题
        client = get_jira_client()
        issue = client.issue(issue_key)
        issue.update(fields=fields)
        
        # 获取更新后的问题
        updated_issue = client.issue(issue_key)
        return format_issue(updated_issue)
    except Exception as e:
        logger.error(f"更新问题 {issue_key} 失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="获取JIRA项目列表",
)
def get_projects() -> Dict[str, Any]:
    """获取所有项目列表.
    
    Returns:
        Dict[str, Any]: 项目列表
    """
    logger.info("获取项目列表")
    try:
        client = get_jira_client()
        projects = client.projects()
        
        result = [
            {
                "id": project.id,
                "key": project.key,
                "name": project.name,
                "lead": getattr(project, "lead", {}).get("displayName", ""),
            }
            for project in projects
        ]
        
        return {"projects": result}
    except Exception as e:
        logger.error(f"获取项目列表失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="获取JIRA项目详情",
)
def get_project(
    project_key: str
) -> Dict[str, Any]:
    """获取项目详情.
    
    Args:
        project_key: 项目键
    
    Returns:
        Dict[str, Any]: 项目详情
    """
    logger.info(f"获取项目: {project_key}")
    try:
        client = get_jira_client()
        project = client.project(project_key)
        
        return {
            "id": project.id,
            "key": project.key,
            "name": project.name,
            "lead": getattr(project, "lead", {}).get("displayName", ""),
            "description": getattr(project, "description", ""),
            "url": project.self,
        }
    except Exception as e:
        logger.error(f"获取项目 {project_key} 失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="调试JIRA问题字段",
)
def debug_issue_fields(
    issue_key: str,
) -> Dict[str, Any]:
    """查看JIRA问题的字段结构，用于调试.
    
    Args:
        issue_key: JIRA问题键
    
    Returns:
        Dict[str, Any]: 字段结构信息
    """
    logger.info(f"调试问题字段: {issue_key}")
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        
        fields = []
        for field_name in dir(issue.fields):
            if field_name.startswith('_') or callable(getattr(issue.fields, field_name)):
                continue
                
            value = getattr(issue.fields, field_name)
            field_type = type(value).__name__
            
            if field_name in ('attachment', 'attachments'):
                if value:
                    attachment_info = []
                    for att in value:
                        attachment_info.append({
                            "id": getattr(att, "id", None),
                            "filename": getattr(att, "filename", None),
                            "size": getattr(att, "size", None),
                            "content_type": getattr(att, "mimeType", None),
                            "created": getattr(att, "created", None),
                        })
                    fields.append({"name": field_name, "type": field_type, "value": attachment_info})
                else:
                    fields.append({"name": field_name, "type": field_type, "value": None})
            else:
                # 对于其他字段，仅显示类型信息和简单值
                simple_value = str(value)[:100] if value is not None else None
                fields.append({"name": field_name, "type": field_type, "preview": simple_value})
        
        return {
            "id": issue.id,
            "key": issue.key,
            "fields": sorted(fields, key=lambda x: x["name"])
        }
    except Exception as e:
        logger.error(f"调试问题 {issue_key} 字段失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="根据问题ID和文件名获取JIRA附件",
)
def get_attachment_by_filename(
    issue_key: str,
    filename: str,
    save_to_disk: bool = True,
) -> Dict[str, Any]:
    """根据问题ID和文件名获取JIRA附件.
    
    Args:
        issue_key: JIRA问题键
        filename: 附件文件名
        save_to_disk: 是否保存到本地磁盘
    
    Returns:
        Dict[str, Any]: 附件内容
    """
    logger.info(f"根据文件名获取附件: issue={issue_key}, filename={filename}")
    try:
        # 使用JIRA REST API直接获取问题附件
        client = get_jira_client()
        
        # 获取问题详情
        issue_url = f"{jira_settings.server_url}/rest/api/2/issue/{issue_key}"
        response = client._session.get(issue_url)
        if response.status_code != 200:
            return {"error": f"获取问题失败: {response.text}"}
            
        issue_data = response.json()
        
        # 检查附件
        attachments = issue_data.get("fields", {}).get("attachment", [])
        if not attachments:
            return {"error": f"问题 {issue_key} 没有附件"}
            
        # 查找指定文件名的附件
        attachment = None
        for att in attachments:
            if att.get("filename") == filename:
                attachment = att
                break
                
        if not attachment:
            return {"error": f"未找到名为 {filename} 的附件"}
            
        # 获取附件内容
        attachment_url = attachment.get("content")
        if not attachment_url:
            return {"error": "附件URL不存在"}
            
        # 下载附件
        response = client._session.get(attachment_url)
        if response.status_code != 200:
            return {"error": f"下载附件失败: {response.text}"}
            
        content = response.content
        mime_type = attachment.get("mimeType", "application/octet-stream")
        
        result = {
            "id": attachment.get("id"),
            "filename": filename,
            "size": len(content),
            "content_type": mime_type,
            "created": attachment.get("created"),
        }
        
        # 如果要保存到磁盘
        if save_to_disk:
            file_path = get_attachment_path(issue_key, filename)
            with open(file_path, "wb") as f:
                f.write(content)
            result["local_path"] = file_path
        
        # 处理不同的内容类型
        if mime_type.startswith("image/"):
            # 对于图片，返回Base64编码
            result["content"] = base64.b64encode(content).decode('utf-8')
            result["encoding"] = "base64"
        elif mime_type.startswith("text/"):
            # 对于文本文件，直接返回文本内容
            try:
                result["content"] = content.decode('utf-8')
                result["encoding"] = "text"
            except UnicodeDecodeError:
                # 如果解码失败，回退到Base64
                result["content"] = base64.b64encode(content).decode('utf-8')
                result["encoding"] = "base64"
        else:
            # 对于其他类型，返回Base64编码
            result["content"] = base64.b64encode(content).decode('utf-8')
            result["encoding"] = "base64"
        
        return result
    except Exception as e:
        logger.error(f"获取问题 {issue_key} 的附件 {filename} 失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="获取JIRA问题及其附件",
)
def getIssues(
    issue_key: str,
) -> Dict[str, Any]:
    """获取JIRA问题及其附件信息.
    
    Args:
        issue_key: JIRA问题键
    
    Returns:
        Dict[str, Any]: 问题详情及附件信息
    """
    logger.info(f"获取问题及附件: {issue_key}")
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        
        # 使用format_issue函数来获取JSON可序列化的问题数据
        issue_data = format_issue(issue)
        
        # 确保附件列表为JSON可序列化对象
        return issue_data
    except Exception as e:
        logger.error(f"获取问题 {issue_key} 及附件失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="下载JIRA问题的所有附件到本地",
)
def download_all_attachments(
    issue_key: str,
) -> Dict[str, Any]:
    """下载JIRA问题的所有附件到本地.
    
    Args:
        issue_key: JIRA问题键
    
    Returns:
        Dict[str, Any]: 下载结果
    """
    logger.info(f"下载问题所有附件: {issue_key}")
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        
        downloads = []
        failed = []
        
        # 获取附件列表
        attachments = []
        if hasattr(issue.fields, "attachment") and issue.fields.attachment:
            attachments = issue.fields.attachment
        
        if not attachments:
            return {
                "issue_key": issue_key,
                "message": "此问题没有附件",
                "total": 0,
                "downloads": []
            }
        
        # 为此问题创建目录
        issue_dir = os.path.join(ATTACHMENTS_DIR, issue_key)
        os.makedirs(issue_dir, exist_ok=True)
        
        # 下载每个附件
        for attachment in attachments:
            try:
                file_path = os.path.join(issue_dir, attachment.filename)
                
                # 下载内容
                content = attachment.get()
                
                # 保存到文件
                with open(file_path, "wb") as f:
                    f.write(content)
                
                downloads.append({
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "size": os.path.getsize(file_path),
                    "content_type": attachment.mimeType,
                    "local_path": file_path
                })
            except Exception as e:
                logger.error(f"下载附件 {attachment.filename} 失败: {str(e)}")
                failed.append({
                    "filename": attachment.filename,
                    "error": str(e)
                })
        
        return {
            "issue_key": issue_key,
            "total": len(attachments),
            "success": len(downloads),
            "failed": len(failed),
            "download_dir": issue_dir,
            "downloads": downloads,
            "failures": failed if failed else None
        }
    except Exception as e:
        logger.error(f"下载问题 {issue_key} 的所有附件失败: {str(e)}")
        return {"error": str(e)}


@mcp.tool(
    description="获取JIRA问题的所有附件",
)
def get_issue_attachments(
    issue_key: str,
    download: bool = False
) -> Dict[str, Any]:
    """获取JIRA问题的所有附件信息.
    
    Args:
        issue_key: JIRA问题键
        download: 是否下载附件到本地
    
    Returns:
        Dict[str, Any]: 附件列表
    """
    logger.info(f"获取问题附件列表: {issue_key}, download={download}")
    
    if download:
        return download_all_attachments(issue_key)
    
    try:
        client = get_jira_client()
        issue = client.issue(issue_key)
        
        attachments = []
        if hasattr(issue.fields, "attachment") and issue.fields.attachment:
            for attachment in issue.fields.attachment:
                # 检查附件是否已存在于本地
                local_path = get_attachment_path(issue_key, attachment.filename)
                exists_locally = os.path.exists(local_path)
                
                attachments.append({
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "size": attachment.size,
                    "content_type": attachment.mimeType,
                    "created": str(attachment.created),  # 确保日期是字符串
                    "url": str(attachment.content),  # 确保URL是字符串
                    "local_path": local_path if exists_locally else None,
                    "exists_locally": exists_locally
                })
        
        return {
            "issue_key": issue_key,
            "attachments": attachments,
            "total": len(attachments),
            "attachments_dir": os.path.join(ATTACHMENTS_DIR, issue_key)
        }
    except Exception as e:
        logger.error(f"获取问题 {issue_key} 附件列表失败: {str(e)}")
        return {"error": str(e)}


def main():
    """主函数."""
    parser = argparse.ArgumentParser(description="Run the JIRA MCP Server")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--transport", "-t", choices=["sse", "stdio"], default="stdio")
    
    args = parser.parse_args()
    
    try:
        # 检查环境变量
        if not jira_settings.server_url:
            logger.warning("未设置JIRA_SERVER_URL环境变量")
        
        if not jira_settings.username:
            logger.warning("未设置JIRA_USERNAME环境变量")
        
        if not jira_settings.password and not jira_settings.api_token:
            logger.warning("未设置JIRA_PASSWORD或JIRA_API_TOKEN环境变量")
        
        # 运行MCP服务器
        logger.info(f"Starting JIRA MCP Server with {args.transport} transport")
        mcp.run(transport=args.transport)
    except Exception as e:
        logger.error(f"Error starting JIRA MCP Server: {str(e)}")
        raise


if __name__ == "__main__":
    main() 