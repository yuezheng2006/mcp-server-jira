#!/usr/bin/env python3
import json
import argparse
from src.server import get_issue_attachments

def main():
    parser = argparse.ArgumentParser(description="获取JIRA问题的所有附件信息")
    parser.add_argument("issue_key", help="JIRA问题键")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    print(f"获取问题 {args.issue_key} 的附件列表...")
    result = get_issue_attachments(args.issue_key)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    print(f"问题 {args.issue_key} 有 {result['total']} 个附件")
    
    for i, attachment in enumerate(result["attachments"], 1):
        print(f"{i}. {attachment['filename']} - {attachment['size']} 字节, {attachment['content_type']}")
        print(f"   URL: {attachment['url']}")
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"附件信息已保存至: {args.output}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 