
import os
import sys
import traceback
import re
import logging
from pathlib import Path
from fbx import*
from colorama import Fore, Back, Style, init

from .fbx_utility import*
from .texconv_wrapper import TexConvWrapper as TexConv
from .cfg_materials import load_material_info, load_all_materials
from .dds_to_dds_converter import DDStoXFormatter
from .texture_integrator import TextureIntegrator
from .pbr_converter import BlinnPhongToPBRConverter, create_pbr_params_from_ini_dict
from .pbr_material_applier import PBRMaterialApplier, find_material_by_name
from dds_formater import is_r8g8, is_r8

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
    if (is_r8g8(file_path)):
        out_map = 'in0'


def create_convert_to_non_alpha() -> str:
    """ Create new texture without alpha chanel.If failed to create texture,return original texture instead.
    """
    new_old_dic =  {}
    def convert(tex :FbxFileTexture,parent_fldr :str) -> str:
        tex_path = tex.GetFileName()
        if tex_path in new_old_dic:
            return new_old_dic[tex_path]
        

        file_path = Path(tex_path)
        out_file_name = file_path.stem + '_new' + '.png'
        out_file_path = parent_fldr / out_file_name
        

        try:
            in_map = 'rgb'
            out_map = 'in0.rgb'
            input_texture_path = str(file_path)
            
            # is_r8g8の場合、DXT1に変換
            if (is_r8g8(file_path)):
                # 出力ディレクトリを parent_fldr に指定し、-sx で接尾辞を付加する
                sx_suffix = '_dxt1'
                dds_converter = DDStoXFormatter()

                dds_converter.convert(
                    input_dds=str(file_path),
                    output_dds=str(parent_fldr),
                    format="DXT1",
                    overwrite=True,
                    sx=sx_suffix,
                )
                # TexConv により出力されるファイル名は入力ベース名 + sx + .dds
                dxt1_file_path = parent_fldr / (file_path.stem + sx_suffix + '.dds')
                logger.info(f"Converted R8G8 to DXT1: {file_path} -> {dxt1_file_path}")

                # DXT1変換後のテクスチャを入力として使用
                input_texture_path = str(dxt1_file_path)
                in_map = 'rgb'
                out_map = 'in0.rrr'
            
            # is_r8の場合、グレースケール値をRGBに複製
            elif (is_r8(file_path)):
                # 出力ディレクトリを parent_fldr に指定し、-sx で接尾辞を付加する
                sx_suffix = '_r8_to_rgb'
                dds_converter = DDStoXFormatter()

                dds_converter.convert(
                    input_dds=str(file_path),
                    output_dds=str(parent_fldr),
                    format="DXT1",
                    overwrite=True,
                    sx=sx_suffix,
                )
                # TexConv により出力されるファイル名は入力ベース名 + sx + .dds
                r8_converted_path = parent_fldr / (file_path.stem + sx_suffix + '.dds')
                logger.info(f"Converted R8 to DXT1: {file_path} -> {r8_converted_path}")

                # グレースケール値をRGBのすべてのチャンネルに複製
                input_texture_path = str(r8_converted_path)
                in_map = 'r'
                out_map = 'in0.rrr'
            
            TexConv(r".\.tools\ezTexConv.exe")\
                .add_input(0, input_texture_path)\
                .set_output(str(out_file_path))\
                .set_channel_map(in_map, out_map)\
                .run()
                
        except Exception as e:
            logger.warning(f'Failed to create new texture for "{file_path}".Texture will be use same one.For more debug infomation,read log at logs folder.')
            logger.debug(e)
            new_texture_failed_list.append(file_path)
            return str(file_path)
        new_old_dic[tex_path] = str(out_file_path)
        return str(out_file_path)
    return convert

def main_process(manager :FbxManager,scene :FbxScene,main_fldr_path :Path,mat_info :dict[str,bool]) -> bool:
    """
    メイン処理
    
    Returns:
        bool: 処理が成功したか（全てのステップが成功）
    """
    logger.info(Fore.YELLOW + 'Start main fix process')
    process_success = True  # 全体の成功フラグ
    
    #Node→Material→property(diffuse)→Texsture
    #新規テクスチャのフォルダーを作成
    new_texture_fldr = main_fldr_path / 'new_texture'
    new_texture_fldr.mkdir(exist_ok=True)

    root_node = scene.GetRootNode()
    nodes = node_recursion(root_node)
    mats = {str(mat.GetNameOnly()) : mat  for node in nodes if (mat := node.GetMaterial(0))}
    # 透明マテリアルの透明度を明示的に設定
    transparent_mats = [ (mat_name, mat) for mat_name, mat in mats.items() if (mat_info[mat_name] == True) ]
    for mat_name, mat in transparent_mats:
        try:
            prop_trans = mat.FindProperty(FbxSurfaceMaterial.sTransparencyFactor)
            if prop_trans.IsValid():
                prop_trans.Set(1.0)
                logger.debug(f"Set sTransparencyFactor=1 for transparent material: {mat_name}")
            else:
                logger.warning(f"sTransparencyFactor property not found for material: {mat_name}")
        except Exception as e:
            logger.warning(f"Failed to set transparency for {mat_name}: {e}")
    non_transparent_mat = [mat for mat_name,mat in mats.items() if (mat_info[mat_name] == False)]
    props = [mat and mat.FindProperty(FbxSurfaceMaterial.sDiffuse) for mat in non_transparent_mat]

    srcs = [prop and prop.GetSrcObject(0) for prop in props]
    texs : list[FbxFileTexture] = [isinstance(src, FbxFileTexture) and src for src in srcs]
    
    # 非透過テクスチャのアルファ抜きテクスチャを生成
    logger.info(Fore.YELLOW + 'Start convert texture...')
    convert_to_non_alpha = create_convert_to_non_alpha()
    new_tex_paths = [tex and convert_to_non_alpha(tex, new_texture_fldr) for tex in texs]
    failed_count = len(new_texture_failed_list)
    if(failed_count > 0):
        process_success = False
        logger.warning(f'Failed to create new texture {failed_count} times.Below is the list of failed texture paths')
        [print(str(path)) for path in new_texture_failed_list]
    else :
        logger.info('[SUCCESS] Success to convert texture')
    
    for (prop,old_tex,new_tex) in zip(props,texs,new_tex_paths,strict=True):
        if prop and old_tex and new_tex:
            prop.DisconnectSrcObject(old_tex)
            tex = FbxFileTexture.Create(scene, old_tex.GetFileName())
            tex.SetFileName(new_tex)
            tex.SetTextureUse(FbxTexture.ETextureUse.eStandard)
            tex.SetMappingType(FbxTexture.EMappingType.eUV)
            tex.SetMaterialUse(FbxFileTexture.EMaterialUse.eModelMaterial)
            tex.SetSwapUV(False)
            tex.SetTranslation(0.0, 0.0)
            tex.SetScale(1.0, 1.0)
            tex.SetRotation(0.0, 0.0)
            prop.ConnectSrcObject(tex)
    logger.info('[SUCCESS] Success to texture replacement')
    
    # === PBR テクスチャ変換・適用処理 ===
    logger.info(Fore.YELLOW + 'Start PBR conversion and application...')
    pbr_error_count = 0
    try:
        # テクスチャ変換フォルダを設定
        pbr_texture_folder = main_fldr_path / 'pbr_textures'
        pbr_texture_folder.mkdir(exist_ok=True)
        
        # マテリアル詳細情報を読み込み
        all_materials = load_all_materials(main_fldr_path)
        
        # テクスチャインテグレータを初期化
        integrator = TextureIntegrator(pbr_texture_folder)
        
        # PBRコンバータを初期化
        converter = BlinnPhongToPBRConverter()
        
        # PBRマテリアルアプライアを初期化
        pbr_applier = PBRMaterialApplier(scene)
        
        # 各マテリアルを処理
        pbr_results = {}
        for mat_name, mat_info in all_materials.items():
            logger.debug(f"Processing material for PBR: {mat_name}")
            
            # PBRパラメータを計算
            bp_params = create_pbr_params_from_ini_dict({
                'SHADER': mat_info.shader,
                'ksDiffuse': mat_info.ks_diffuse,
                'ksSpecular': mat_info.ks_specular,
                'ksSpecularEXP': mat_info.ks_specular_exp,
                'ksEmissive': mat_info.ks_emissive,
                'ksAmbient': mat_info.ks_ambient,
                'ksAlphaRef': mat_info.ks_alpha_ref,
                'ALPHABLEND': 1 if mat_info.alpha_blend else 0,
                'ALPHATEST': 1 if mat_info.alpha_test else 0,
            })
            pbr_params = converter.convert(bp_params)
            
            # テクスチャを変換
            texture_paths = integrator.convert_all_textures(
                mat_info,
                pbr_params,
                mat_name
            )
            
            # FBX マテリアルに PBR を適用
            fbx_material = find_material_by_name(root_node, mat_name)
            if fbx_material:
                success = pbr_applier.apply_pbr_to_material(
                    fbx_material,
                    pbr_params,
                    texture_paths
                )
                pbr_results[mat_name] = success
                
                # カスタムプロパティ追加
                pbr_applier.add_custom_properties(fbx_material, mat_info)
            else:
                logger.warning(f"Material not found in FBX: {mat_name}")
                pbr_results[mat_name] = False
        
        # 結果サマリー
        success_count = sum(1 for v in pbr_results.values() if v)
        pbr_error_count = len(pbr_results) - success_count
        
        if pbr_error_count > 0:
            process_success = False
            logger.warning(
                f'[WARNING] PBR applied to {success_count}/{len(pbr_results)} materials ({pbr_error_count} errors)'
            )
        else:
            logger.info(
                f'[SUCCESS] PBR applied to {success_count}/{len(pbr_results)} materials'
            )
        
    except Exception as e:
        process_success = False
        pbr_error_count += 1
        logger.error(f'Error during PBR conversion: {e}')
        logger.debug(traceback.format_exc())
    
    if process_success:
        logger.info('[SUCCESS] Success to main fix process')
    else:
        logger.error('[FAILED] Some steps did not complete successfully')
        logger.warning(f'  - Texture conversion errors: {len(new_texture_failed_list)}')
        logger.warning(f'  - PBR application errors: {pbr_error_count}')
    
    return process_success

def run_material_fix(fldr_path:Path) -> int:
    """
    マテリアル修正パイプラインを実行
    
    Returns:
        int: 終了コード (0: 成功, 1: 警告があるが完了, 2: エラーで失敗)
    """
    logger.info(Fore.YELLOW + f'Start fix fbx')
    exit_code = 0
    
    # fbxの入出力パス設定
    fbx_path = list(fldr_path.glob('*.fbx'))[0]
    out_fbx_path  = str(EXPORT_FOLDER / Path(fbx_path.stem + '_new' + fbx_path.suffix))
    
    # Logging
    logger.info(f'fbx_path:{fbx_path}')
    logger.info(f'out_fbx_path:{out_fbx_path}')

    mat_info = load_material_info(fldr_path)
    # インポート→メインプロセス→エクスポート
    manager = None
    try:
        manager, scene = setup_with_import(str(fbx_path))
        
        # メイン処理を実行して戻り値を受け取る
        main_process_success = main_process(manager, scene, fldr_path, mat_info)
        
        # FBX をエクスポート
        export(manager, scene, out_fbx_path)
        logger.info(Fore.GREEN + '[SUCCESS] Sucsess to export fbx')
        
        # メイン処理にエラーがあった場合は終了コード 1
        if not main_process_success:
            exit_code = 1
            error_msg = 'FAILED: FBX has been modified but with errors. Please review the log file.'
            logger.error(f'[ERROR] {error_msg}')
            print(f"\n[ERROR] {error_msg}")
        else:
            exit_code = 0
            success_msg = 'Success: FBX has been fixed successfully.'
            logger.info(f'[SUCCESS] {success_msg}')
            print(f"\n[SUCCESS] {success_msg}")
            
    except Exception as e:
        exit_code = 2
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
        logger.error(Fore.RED + f'✗ CRITICAL ERROR: Failed to fix fbx: {e}', stack_info=True)
    finally:
        if manager is not None:
            manager.Destroy()
    
    # Flush all logging handlers to ensure logs are written before exit
    try:
        for handler in list(logger.handlers):
            if hasattr(handler, 'flush'):
                handler.flush()
        for handler in list(logging.root.handlers):
            if hasattr(handler, 'flush'):
                handler.flush()
    except Exception as flush_error:
        print(f"Warning: Failed to flush logging handlers: {flush_error}")
    
    return exit_code