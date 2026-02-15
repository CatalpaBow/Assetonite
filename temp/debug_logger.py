#!/usr/bin/env python
"""ログ設定の診断スクリプト"""

from pathlib import Path
import sys

src = Path(__file__).parent / 'src'
sys.path.insert(0, str(src))

from utils.logger_getter import get_logger
import logging

# ログ設定情報を表示
logger = get_logger('fix_fbx')

print("=" * 80) 
print("Logger Configuration Debug")
print("=" * 80)

print(f"\nLogger name: {logger.name}")
print(f"Logger level: {logger.level} ({logging.getLevelName(logger.level)})")
print(f"Logger propagate: {logger.propagate}")

print(f"\nHandlers ({len(logger.handlers)}):")
for i, handler in enumerate(logger.handlers):
    print(f"  {i+1}. {handler.__class__.__name__}")
    print(f"     Level: {handler.level} ({logging.getLevelName(handler.level)})")
    if hasattr(handler, 'baseFilename'):
        print(f"     File: {handler.baseFilename}")
    if hasattr(handler, 'formatter'):
        print(f"     Format: {handler.formatter._fmt if handler.formatter else 'None'}")

print("\n" + "=" * 80)
print("Testing log output")
print("=" * 80)

# テスト出力
logger.debug("DEBUG message")
logger.info("INFO message")
logger.warning("WARNING message")
logger.error("ERROR message")

print("\nCheck if log file was created and contains messages...")
print("Recent log files:")
logs_dir = Path('logs')
if logs_dir.exists():
    log_files = list(logs_dir.glob('fixFbx_*.log'))
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for i, f in enumerate(log_files[:3]):
        size = f.stat().st_size
        print(f"  {i+1}. {f.name:40} {size:10} bytes")
        
        # 最新ファイルの内容を表示
        if i == 0:
            print(f"\nContent of {f.name}:")
            print("-" * 80)
            with open(f, 'r') as logf:
                content = logf.read()
                if content:
                    print(content[-500:])  # 最後500文字
                else:
                    print("[Empty file]")
            print("-" * 80)
