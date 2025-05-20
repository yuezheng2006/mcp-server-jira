#!/usr/bin/env python3
import base64
import argparse
import os
from src.server import get_attachment_by_filename

def main():
    parser = argparse.ArgumentParser(description="提取JIRA问题的附件")
    parser.add_argument("issue_key", help="JIRA问题键")
    parser.add_argument("filename", help="附件文件名")
    parser.add_argument("--output", "-o", help="输出文件名")
    parser.add_argument("--no-save", action="store_true", help="不保存到~/.jira_mcp目录")
    
    args = parser.parse_args()
    
    print(f"获取问题 {args.issue_key} 的附件 {args.filename}...")
    result = get_attachment_by_filename(args.issue_key, args.filename, save_to_disk=not args.no_save)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    if "local_path" in result:
        print(f"附件已保存到: {result['local_path']}")
    
    if args.output:
        # 如果指定了输出文件，再次保存一份
        content = base64.b64decode(result["content"]) if result["encoding"] == "base64" else result["content"].encode('utf-8')
        with open(args.output, "wb") as f:
            f.write(content)
        print(f"附件已另存为: {args.output}")
    
    print(f"文件类型: {result['content_type']}")
    print(f"文件大小: {result['size']} 字节")
    print(f"创建时间: {result['created']}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 