#!/usr/bin/env python
"""GT86 テスト実行スクリプト"""

from pathlib import Path
import sys

# プロジェクトの src をパスに追加
src = Path(__file__).parent / 'src'
sys.path.insert(0, str(src))

from utils.logger_getter import get_logger
logger = get_logger('run_test')

def main():
    logger.info("=" * 70)
    logger.info("GT86 Sample Test Execution")
    logger.info("=" * 70)
    
    # テスト1: インポート確認
    logger.info("\n[Test 1] Importing modules...")
    try:
        from fbx_fixer.cfg_materials import load_all_materials
        logger.info("  ✓ cfg_materials imported")
        
        from fbx_fixer.pbr_converter import BlinnPhongToPBRConverter, create_pbr_params_from_ini_dict
        logger.info("  ✓ pbr_converter imported")
        
        from fbx_fixer.texture_integrator import TextureIntegrator
        logger.info("  ✓ texture_integrator imported")
        
        from fbx_fixer.pbr_material_applier import PBRMaterialApplier
        logger.info("  ✓ pbr_material_applier imported")
        
        from fbx_fixer.material_fixer import run_material_fix
        logger.info("  ✓ material_fixer imported")
        
    except ImportError as e:
        logger.error(f"  ✗ Import error: {e}")
        return False
    
    # テスト2: GT86パス確認
    logger.info("\n[Test 2] Checking GT86 path...")
    gt86_path = Path(__file__).parent / "data" / "input" / "fbx_fixer" / "gt86"
    status = "exists" if gt86_path.exists() else "NOT FOUND"
    logger.info(f"  GT86 path: {gt86_path} ({status})")
    
    if not gt86_path.exists():
        logger.warning("  GT86 test data not available - skipping material tests")
        return True
    
    # テスト3: マテリアル読み込み
    logger.info("\n[Test 3] Loading materials...")
    try:
        materials = load_all_materials(gt86_path)
        logger.info(f"  ✓ Loaded {len(materials)} materials")
        
        # 最初の3つを表示
        for i, (name, mat) in enumerate(list(materials.items())[:3]):
            logger.info(f"    - {name}: {mat.shader}")
        
    except Exception as e:
        logger.error(f"  ✗ Failed to load materials: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # テスト4: マテリアル修正パイプライン
    logger.info("\n[Test 4] Running material fix pipeline...")
    try:
        # data/output/pbr_textures フォルダが存在することを確認
        output_folder = Path(__file__).parent / "data" / "output" / "pbr_textures"
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # パイプライン実行
        run_material_fix(gt86_path)
        logger.info("  ✓ Material fix pipeline completed")
        
    except Exception as e:
        logger.error(f"  ✗ Material fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ ALL TESTS PASSED")
    logger.info("=" * 70)
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
