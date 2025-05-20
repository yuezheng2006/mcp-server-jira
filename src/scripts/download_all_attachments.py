#!/usr/bin/env python3
"""JIRA附件下载工具."""
import json
import argparse
from src.server import download_all_attachments, get_issue_attachments

def main():
    """命令行入口函数."""
    parser = argparse.ArgumentParser(description="管理JIRA问题的附件")
    parser.add_argument("issue_key", help="JIRA问题键")
    parser.add_argument("--list-only", "-l", action="store_true", help="仅列出附件，不下载")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 无论是否下载，都需要先获取附件列表
    print(f"获取问题 {args.issue_key} 的附件列表...")
    result = get_issue_attachments(args.issue_key)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    # 如果只是列出附件
    if args.list_only:
        print(f"问题 {args.issue_key} 共有 {result['total']} 个附件")
        print(f"存储目录: {result['attachments_dir']}")
        print("="*50)
        for i, attachment in enumerate(result["attachments"], 1):
            print(f"{i}. {attachment['filename']} - {attachment['size']} 字节, {attachment['content_type']}")
            if attachment.get('exists_locally'):
                print(f"   [已下载] {attachment['local_path']}")
            else:
                print(f"   [未下载] {attachment['url']}")
                
        # 如果指定了输出文件
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"附件信息已保存至: {args.output}")
            
        return 0
    
    # 否则下载附件
    print(f"正在下载问题 {args.issue_key} 的所有附件...")
    result = download_all_attachments(args.issue_key)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    print(f"下载完成，共 {result['total']} 个附件，成功: {result['success']}，失败: {result['failed']}")
    
    if result['success'] > 0:
        print(f"下载目录: {result['download_dir']}")
        for i, download in enumerate(result["downloads"], 1):
            print(f"{i}. {download['filename']} - {download['size']} 字节, {download['content_type']}")
            print(f"   保存路径: {download['local_path']}")
    
    if result.get('failures'):
        print("\n下载失败的附件:")
        for i, failure in enumerate(result["failures"], 1):
            print(f"{i}. {failure['filename']} - {failure['error']}")
    
    # 如果指定了输出文件
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"下载结果已保存至: {args.output}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 