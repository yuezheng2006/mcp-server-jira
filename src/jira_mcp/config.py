"""JIRA MCP配置模块."""

import os
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class JiraSettings:
    """JIRA连接设置."""
    server_url: str 
    username: str
    password: str = ""
    api_token: str = ""


def load_config(config_path: str = None) -> JiraSettings:
    """加载配置，优先从config文件加载，其次是环境变量.
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        JiraSettings: JIRA配置
    """
    # 优先从config文件加载
    if config_path:
        try:
            config_path = Path(config_path)
            if config_path.exists():
                with open(config_path) as f:
                    config_data = json.load(f)
                    env_vars = config_data.get('env', {})
                    
                    return JiraSettings(
                        server_url=env_vars.get("JIRA_SERVER_URL", os.environ.get("JIRA_SERVER_URL", "")),
                        username=env_vars.get("JIRA_USERNAME", os.environ.get("JIRA_USERNAME", "")),
                        password=env_vars.get("JIRA_PASSWORD", os.environ.get("JIRA_PASSWORD", "")),
                        api_token=env_vars.get("JIRA_API_TOKEN", os.environ.get("JIRA_API_TOKEN", ""))
                    )
        except Exception as e:
            logger.warning(f"Failed to load config file, fallback to env vars: {str(e)}")
    
    # 从环境变量加载
    return JiraSettings(
        server_url=os.environ.get("JIRA_SERVER_URL", ""),
        username=os.environ.get("JIRA_USERNAME", ""),
        password=os.environ.get("JIRA_PASSWORD", ""),
        api_token=os.environ.get("JIRA_API_TOKEN", "")
    )


# 创建JIRA设置实例
jira_settings = load_config()


def get_jira_auth():
    """获取JIRA认证信息.

    Returns:
        tuple: 包含用户名和密码/API令牌的元组
        
    Raises:
        ValueError: 如果认证信息不完整
    """
    password = jira_settings.password or jira_settings.api_token
    if not jira_settings.server_url or not jira_settings.username or not password:
        raise ValueError(
            "JIRA连接信息不完整，请设置以下环境变量: "
            "JIRA_SERVER_URL, JIRA_USERNAME, 以及 JIRA_PASSWORD 或 JIRA_API_TOKEN"
        )
    return (jira_settings.username, password) 