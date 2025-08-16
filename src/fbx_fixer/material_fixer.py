
import os
import sys
import traceback
import re
from pathlib import Path
from fbx import*
from colorama import Fore, Back, Style, init

from .fbx_utility import*
from .texconv_wrapper import TexConvWrapper as TexConv
from .cfg_materials import load_material_info
from src.dds_formater import dds_old_formater

sys.path.append(os.path.curdir)
from src.utils.logger_getter import get_logger
logger = get_logger('fix_fbx')
EXPORT_FOLDER = Path(__file__).absolute().parent.parent.parent  / 'data' / 'output' / 'fbx_fixer'
#ksBrokenGlassはアルファ抜きをする
#ksPerPixelMultiMapだとエラーが起きる　フォーマットが R8G8_UNORM　で変換エラー? isAdditiveオプションが影響している？

new_texture_failed_list = []
def setup_with_import(fbx_path :str) -> tuple[FbxManager, FbxScene]:
    logger.info(Fore.YELLOW + 'start import fbx')
    # Configure New Scene
    manager = FbxManager.Create()
    ios = FbxIOSettings.Create(manager, IOSROOT) # IOSN_EXPORT
    manager.SetIOSettings(ios)

    importer = FbxImporter.Create(manager,'')
    if not(importer.Initialize(fbx_path,-1,manager.GetIOSettings())):
        raise RuntimeError(f"Failed to initialize importer for '{fbx_path}'")

    scene = FbxScene.Create(manager,'scene')
    if not(importer.Import(scene)):
        raise RuntimeError(f"Failed to import scene from '{fbx_path}'")
    importer.Destroy()
    logger.info(Fore.GREEN + 'sucsess to fbx import')
    return (manager,scene)

def export(manager :FbxManager,scene :FbxScene,out_path :str) -> None:
    #エクスポート
    exporter = FbxExporter.Create(manager,'')
    if not(exporter.Initialize(out_path,-1,manager.GetIOSettings())):
        raise RuntimeError(f"Faield to initialize exporter for '{out_path}'")
    else:
        exporter.Export(scene)
        logger.info(Fore.GREEN  + 'Sucsess to export fbx')
  


def in_out_setter(file_path : Path):
    out_map = 'in0.rgb'
    in_map = 'rgb'
    if (dds_old_formater.is_r8g8(file_path)):
        out_map = 'in0'

def convert_to_non_alpha(tex :FbxFileTexture,parent_fldr :str,new_old_dic : dict[str,str]) -> str:
    """ Create new texture without alpha chanel.If failed to create texture,return original texture instead.
    """
    tex_path = tex.GetFileName()
    if tex_path in new_old_dic:
        return new_old_dic[tex_path]
    

    file_path = Path(tex_path)
    out_file_name = file_path.stem + '_new' + '.png'
    out_file_path = parent_fldr / out_file_name

    try:
        TexConv(r"D:\Devlop\Assetonite\src\libs\ezTexConv.exe")\
            .add_input(0,tex_path)\
            .set_output(str(out_file_path))\
            .set_channel_map('rgb','in0.rgb')\
            .run()
            
    except Exception as e:
        logger.error(f'Failed to create new texture for "{file_path}".Texture will be use same one.For more debug infomation,read hoge at logs folder.')
        logger.debug(e)
        new_texture_failed_list.append(file_path)
        return str(file_path)
    new_old_dic[tex_path] = str(out_file_path)
    return str(out_file_path)

def main_process(manager :FbxManager,scene :FbxScene,main_fldr_path :Path,mat_info :dict[str,bool]) -> None:
    logger.info(Fore.YELLOW + 'Start main fix process')
    #Node→Material→property(diffuse)→Texsture
    #新規テクスチャのフォルダーを作成
    new_texture_fldr = main_fldr_path / 'new_texture'
    new_texture_fldr.mkdir(exist_ok=True)

    root_node = scene.GetRootNode()
    nodes = node_recursion(root_node)
    mats = {str(mat.GetNameOnly()) : mat  for node in nodes if (mat := node.GetMaterial(0))}
    non_transparent_mat = [mat for mat_name,mat in mats.items() if (mat_info[mat_name] == False)]
    props = [mat and mat.FindProperty(FbxSurfaceMaterial.sDiffuse) for mat in non_transparent_mat]

    srcs = [prop and prop.GetSrcObject(0) for prop in props]
    texs : list[FbxFileTexture] = [isinstance(src, FbxFileTexture) and src for src in srcs]
    
    # 非透過テクスチャのアルファ抜きテクスチャを生成
    logger.info(Fore.YELLOW + 'Start convert texture...')
    new_old_dic = {}
    new_tex_paths = [tex and convert_to_non_alpha(tex, new_texture_fldr,new_old_dic) for tex in texs]
    failed_count = len(new_texture_failed_list)
    if(failed_count > 0):
        logger.warning(f'Failed to create new texture {failed_count} times.Below is the list of failed texture paths')
        [print(str(path)) for path in new_texture_failed_list]
    else :
        logger.info(Fore.GREEN  + 'Sucess to convert texture')

    for (prop,old_tex,new_tex) in zip(props,texs,new_tex_paths,strict=True):
        if prop and old_tex and new_tex:
            prop.DisconnectSrcObject(old_tex)
            tex = FbxFileTexture.Create(scene, "NewTexture")
            tex.SetFileName(new_tex)
            tex.SetTextureUse(FbxTexture.ETextureUse.eStandard)
            tex.SetMappingType(FbxTexture.EMappingType.eUV)
            tex.SetMaterialUse(FbxFileTexture.EMaterialUse.eModelMaterial)
            tex.SetSwapUV(False)
            tex.SetTranslation(0.0, 0.0)
            tex.SetScale(1.0, 1.0)
            tex.SetRotation(0.0, 0.0)
            prop.ConnectSrcObject(tex)
    logger.info(Fore.GREEN + 'Sucess to main fix process')

def run_material_fix(fldr_path:Path) -> None:
    logger.info(Fore.YELLOW + f'Start fix fbx')
    #fbxの入出力パス設定
    fbx_path = list(fldr_path.glob('*.fbx'))[0]
    out_fbx_path  = str(EXPORT_FOLDER / Path(fbx_path.stem + '_new' + fbx_path.suffix))
    
    # Logging
    
    logger.info(f'fbx_path:{fbx_path}')
    logger.info(f'out_fbx_path:{out_fbx_path}')

    mat_info = load_material_info(fldr_path)
    #インポート→メインプロセス→エクスポート
    manager,scene = setup_with_import(str(fbx_path))
    try:
        main_process(manager,scene,fldr_path,mat_info)
        export(manager,scene,out_fbx_path)
    except Exception as e:
        error_class = type(e)
        error_description = str(e)
        err_msg = '%s: %s' % (error_class, error_description)
        print(err_msg)
        tb = traceback.extract_tb(sys.exc_info()[2])
        trace = traceback.format_list(tb)
        print('---- traceback ----')
        for line in trace:
            if '~^~' in line:
                print(line.rstrip())
            else:
                text = re.sub(r'\n\s*', ' ', line.rstrip())
                print(text)
        print('-------------------')
        logger.error(f'Failed to fix fbx{e.with_traceback}', stack_info=True)
        return
    finally:
        if manager is not None:
            manager.Destroy()
    logger.info(Fore.GREEN+ f'Sucess to fix fbx')

if __name__ == '__main__':
    print(EXPORT_FOLDER)
    run_material_fix(Path(r"F:\Games\OtherGames\Assetto Corsa\content\cars\ks_nissan_skyline_r34\fbx"))