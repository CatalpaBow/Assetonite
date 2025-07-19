from pathlib import Path
import subprocess
import os
import configparser
from logging import getLogger
CARS_FOLDER = r'F:\Games\OtherGames\Assetto Corsa\content\cars'
KUNOSU_EXE = os.path.expandvars(r'%ProgramFiles(x86)%\KunosSDK\kunossdk.exe')
logger = getLogger('def')

def read_cfg(path : str) -> configparser.ConfigParser:
    try:
        with open(path,'r',encoding='utf-8') as f:
            lines = f.readlines()
        content = [line.split(';')[0] for line in lines]
        content = '\n'.join(content)
        cfg = configparser.ConfigParser()
        cfg.read_string(content)

    except Exception as e:
        logger.error(f'コンフィグファイルの読み込みに失敗しました パス:{path}')
        return None
    else : 
        return cfg

def extract_data_acd(path :Path):
    try:
        subprocess.run([KUNOSU_EXE,path])
    except Exception as e:
        logger.error(f'データ展開失敗:{e}')
    finally:
        logger.info('データ展開成功')

def load_cfg(car_name: str):    
    data_folder_path =  Path(CARS_FOLDER) / car_name / 'data'
    if not(data_folder_path.exists()):
        extract_data_acd(car_name)

    ini_paths = data_folder_path.glob('*.ini')
    cfg_dic = {path.with_suffix('').name : read_cfg(path) for path in ini_paths}

    return ConfigData(cfg_dic)


class ConfigData:
    dic :dict[str,configparser.ConfigParser]
    
    def __init__(self,dic :dict[str, configparser.ConfigParser]):
        self.dic= dic
    def __getitem__(self, key):
        return self.dic[key]