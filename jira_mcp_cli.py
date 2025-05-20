#!/usr/bin/env python3
"""Personal JIRA MCP命令行工具入口点."""

import os
import sys
import argparse

# 导入服务器主函数
from src.jira_mcp.server import main

def cli_main():
    """命令行入口函数."""
    parser = argparse.ArgumentParser(description="Personal JIRA MCP命令行工具")
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