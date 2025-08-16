import subprocess
import configparser

from pathlib import Path
import tomllib
from logging import getLogger

from msg.message_source.i_car_config_loader import BaseCarConifg,ICarConfigLoader
from msg.raw_data.car_config import CarConfig
logger = getLogger('def')
with open('config/.user.toml','rb') as f:
    cfg = tomllib.load(f)
CARS_FOLDER = Path(cfg['path']['assetto_corsa_fldr']) / 'content' / 'cars'
KUNOSU_EXE = Path(cfg['path']['kunosu_exe'])

class ConfigLoaderImplement(ICarConfigLoader):
    @staticmethod
    def read_cfg(path : str) -> configparser.ConfigParser:
        try:
            with open(path,'r',encoding='utf-8') as f:
                lines = f.readlines()
            content = [line.split(';')[0] for line in lines]
            content = '\n'.join(content)
            cfg = configparser.ConfigParser()
            cfg.read_string(content)

        except Exception as e:
            logger.error(f'コンフィグファイルの読み込みに失敗しました パス:{path}\n内容:{e}')
            return None
        else : 
            return cfg
    @staticmethod
    def extract_data_acd(path :Path):
        try:
            subprocess.run([KUNOSU_EXE,path])
        except Exception as e:
            logger.error(f'データ展開失敗:{e}')
        finally:
            logger.info('データ展開成功')

    @staticmethod
    def load(car_name: str) -> BaseCarConifg:    
        logger.info(f'CFG読み込み')
        data_folder_path =  Path(CARS_FOLDER) / car_name / 'data'
        if not(data_folder_path.exists()):
            ConfigLoaderImplement.extract_data_acd(car_name)

        ini_paths = data_folder_path.glob('*.ini')
        cfg_dic = {path.with_suffix('').name : ConfigLoaderImplement.read_cfg(path) for path in ini_paths}

        return CarConfig(cfg_dic)


'''
class ConfigData:
    dic :dict[str,configparser.ConfigParser]
    
    def __init__(self,dic :dict[str, configparser.ConfigParser]):
        self.dic= dic
    def __getitem__(self, key):
        return self.dic[key]
'''