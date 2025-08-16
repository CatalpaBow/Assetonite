from pathlib import Path
from configparser import ConfigParser
import re

def load_cfg(fbx_folder):    
    rslt = list(Path(fbx_folder).glob('*.ini'))
    if(len(rslt) <= 0 ):
        raise RuntimeError(f"ini file not found in {fbx_folder}")    
    cfg_path = rslt[0]
    cfg = ConfigParser()
    cfg.read(cfg_path , encoding='utf-8')
    return cfg

def to_alpha_blend_dic(cfg : ConfigParser):
    mat_sec_list =  [section for section in cfg.sections() if re.fullmatch(r"MATERIAL_\d+", section)]
    mat_dic ={cfg[sec]["NAME"] : int(cfg[sec]["ALPHABLEND"]) > 0 for sec in mat_sec_list}
    return mat_dic

def load_material_info(fbx_folder) :
    cfg = load_cfg(fbx_folder)
    dic = to_alpha_blend_dic(cfg)
    return dic
