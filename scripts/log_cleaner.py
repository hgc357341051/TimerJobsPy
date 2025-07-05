#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志清理脚本
删除runtime/jobs下的所有文件夹
"""

import os
import shutil
from datetime import datetime

def clean_log_files():
    """删除runtime/jobs下的所有文件夹"""
    jobs_dir = "runtime/jobs"
    
    if not os.path.exists(jobs_dir):
        print(f"jobs目录不存在: {jobs_dir}")
        return
    
    # 获取jobs目录下的所有子目录
    subdirs = []
    for item in os.listdir(jobs_dir):
        item_path = os.path.join(jobs_dir, item)
        if os.path.isdir(item_path):
            subdirs.append(item_path)
    
    if not subdirs:
        print("没有找到需要删除的文件夹")
        return
    
    deleted_count = 0
    
    for subdir in subdirs:
        try:
            print(f"删除文件夹: {os.path.basename(subdir)}")
            
            # 递归删除文件夹及其内容
            import shutil
            shutil.rmtree(subdir)
            
            deleted_count += 1
            print(f"  - 删除完成")
            
        except Exception as e:
            print(f"  - 删除失败: {e}")
    
    result = f"文件夹清理完成 - 删除文件夹数: {deleted_count}, 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(result)
    return result

if __name__ == "__main__":
    clean_log_files() 