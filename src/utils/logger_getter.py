from logging import getLogger, StreamHandler, DEBUG ,Formatter,config
import logging
import json
from datetime import datetime
from pathlib import Path

is_already_setuped = False
def _logger_setup():
    with open('config/log_config.json', 'r') as f:
        log_conf = json.load(f)
    
    # ログディレクトリが存在することを確認
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # fixFbxHandler のファイル名を動的に生成（実行毎にタイムスタンプ付きで新規ファイル）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/fixFbx_{timestamp}.log'
    log_conf['handlers']['fixFbxHandler']['filename'] = log_filename
    
    config.dictConfig(log_conf)

def get_logger(name : str):
    global is_already_setuped
    if not is_already_setuped:
        _logger_setup()
        is_already_setuped = True
    return logging.getLogger(name)
