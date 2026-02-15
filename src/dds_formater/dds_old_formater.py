import subprocess
from pathlib import Path
from dataclasses import dataclass
import shutil

dxgi_formats_old = [
    "R32G32B32A32_TYPELESS",
    "R32G32B32_TYPELESS",
    "R16G16B16A16_TYPELESS",
    "R32G32_TYPELESS",
    "R32G8X24_TYPELESS",
    "D32_FLOAT_S8X24_UINT",
    "R32_FLOAT_X8X24_TYPELESS",
    "X32_TYPELESS_G8X24_UINT",
    "R10G10B10A2_TYPELESS",
    "R8G8B8A8_TYPELESS",
    "R16G16_TYPELESS",
    "R32_TYPELESS",
    "D32_FLOAT",
    "R24G8_TYPELESS",
    "D24_UNORM_S8_UINT",
    "R24_UNORM_X8_TYPELESS",
    "X24_TYPELESS_G8_UINT",
    "R8G8_TYPELESS",
    "R16_TYPELESS",
    "R8_TYPELESS",
    "BC1_TYPELESS",
    "BC1_UNORM",
    "BC1_UNORM_SRGB",
    "BC2_TYPELESS",
    "BC2_UNORM",
    "BC2_UNORM_SRGB",
    "BC3_TYPELESS",
    "BC3_UNORM",
    "BC3_UNORM_SRGB",
    "BC4_TYPELESS",
    "BC4_UNORM",
    "BC4_SNORM",
    "BC5_TYPELESS",
    "BC5_UNORM",
    "BC5_SNORM",
]
@dataclass
class DX5Files:
    path : Path


def check_format(path : Path):
    cmd = ['.tools/texdiag.exe','info',str(path)]
    rslt = subprocess.run(cmd,capture_output=True)
    out = rslt.stdout.decode()
    out_lines = out.splitlines()
    format_line = out_lines[9]
    format_line = format_line.replace(' ','')
    format_line = format_line.replace('=','')
    format = format_line.replace('format','')
    return format

def is_new_format(path : Path):
    format = check_format(path)
    return not format in dxgi_formats_old

def to_old_format(file_path : Path ):
    file_path_str = str(file_path)
    out_path = str(file_path.parent)
    exe_path = '.tools/texconv.exe'
    option_list = [
        ['-f','DXT5'],
        ['-o',out_path],
        ['-y']
    ]
    options = sum(option_list,[])

    cmd = [exe_path] + options + [file_path_str]
    rslt = subprocess.run(cmd, capture_output=True)
    print(rslt.stdout.decode("cp932"))

def is_r8g8(path :Path):
    format = check_format(path)
    return 'R8G8_' in format

def is_r8(path :Path):
    format = check_format(path)
    return 'R8_' in format


temp_texsutre_fldr_path = r'F:\Games\OtherGames\Assetto Corsa\content\cars\ke_subaru_impreza_wrx_25bat\fbx\texture'

def test():
    #test_path = '.tools/symbols.dds'
    #rslt_path = to_old_format(test_path)
    #print(rslt_path)
    #is_new_format(path)
    test_fldr_path = Path(r'D:\Devlop\Assetonite\.tools\test_texstures')
    dds_file_paths = Path(test_fldr_path).glob('*.dds')
    new_format_file_paths = list(filter(is_new_format,dds_file_paths))
    
    #バックアップを作成
    backup_path = test_fldr_path / 'backups'
    if not(backup_path.exists()):
        backup_path.mkdir()
    
    [shutil.copy(file_path,backup_path) for file_path in new_format_file_paths]
    print('---TargetFiles---')
    for file_path in new_format_file_paths:
        print(file_path)
        to_old_format(file_path)

def main():
    dds_file_paths = Path(temp_texsutre_fldr_path).glob('*.dds')
    new_format_file_paths = filter(is_new_format,dds_file_paths)
    old_format_files = [to_old_format(file) for file in new_format_file_paths]

if __name__ == '__main__':
    #main()
    test()