#!/usr/bin/env python3
import argparse
from src.server import download_all_attachments, get_issue_attachments

def main():
    parser = argparse.ArgumentParser(description="下载JIRA问题的所有附件")
    parser.add_argument("issue_key", help="JIRA问题键")
    parser.add_argument("--list-only", "-l", action="store_true", help="仅列出附件，不下载")
    
    args = parser.parse_args()
    
    if args.list_only:
        print(f"列出问题 {args.issue_key} 的附件...")
        result = get_issue_attachments(args.issue_key)
    else:
        print(f"正在下载问题 {args.issue_key} 的所有附件...")
        result = download_all_attachments(args.issue_key)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    if args.list_only:
        print(f"问题 {args.issue_key} 共有 {result['total']} 个附件")
        print(f"存储目录: {result['attachments_dir']}")
        print("="*50)
        for i, attachment in enumerate(result["attachments"], 1):
            print(f"{i}. {attachment['filename']} - {attachment['size']} 字节, {attachment['content_type']}")
            if attachment['exists_locally']:
                print(f"   [已下载] {attachment['local_path']}")
            else:
                print(f"   [未下载] {attachment['url']}")
    else:
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
    
    return 0

if __name__ == "__main__":
    exit(main()) 