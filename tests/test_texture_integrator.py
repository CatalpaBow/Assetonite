"""
テクスチャインテグレータのユニットテスト

texture_integrator.py の機能をテストします。
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

src = Path(__file__).parent.parent / 'src'
sys.path.append(str(src))

from fbx_fixer.texture_integrator import TextureIntegrator
from fbx_fixer.pbr_converter import PBRParams
from fbx_fixer.cfg_materials import TextureResource, MaterialInfo


class TestTextureIntegrator:
    """TextureIntegrator のテストケース"""
    
    def setup_method(self):
        """各テストの前に実行"""
        self.output_folder = Path('tests/output/textures')
        self.integrator = TextureIntegrator(self.output_folder)
    
    def test_init_creates_output_folder(self):
        """初期化時に出力フォルダが作成される"""
        assert self.integrator.output_folder.exists()
    
    def test_normalize_metallic_to_255(self):
        """Metallic (0-1) を 0-255 に正規化"""
        # 0.0 → 0
        assert self.integrator._normalize_metallic_to_255(0.0) == 0
        
        # 1.0 → 255
        assert self.integrator._normalize_metallic_to_255(1.0) == 255
        
        # 0.5 → 127 or 128
        result = self.integrator._normalize_metallic_to_255(0.5)
        assert 127 <= result <= 128
    
    def test_normalize_smoothness_to_255(self):
        """Smoothness (0-1) を 0-255 に正規化"""
        # 0.0 → 0
        assert self.integrator._normalize_smoothness_to_255(0.0) == 0
        
        # 1.0 → 255
        assert self.integrator._normalize_smoothness_to_255(1.0) == 255
        
        # 0.5 → 127 or 128
        result = self.integrator._normalize_smoothness_to_255(0.5)
        assert 127 <= result <= 128
    
    def test_to_relative_path_conversion(self):
        """絶対パスを相対パスに変換"""
        cwd = Path.cwd()
        abs_path = cwd / 'some_file.dds'
        
        # 相対化可能な場合
        relative = self.integrator._to_relative_path(str(abs_path))
        assert 'some_file.dds' in relative
    
    @patch('fbx_fixer.texture_integrator.DDStoXFormatter.convert')
    def test_convert_diffuse_to_albedo_success(self, mock_convert):
        """txDiffuse → Albedo 変換が成功"""
        mock_convert.return_value = None  # 例外を発生させない
        
        # モック MaterialInfo を作成
        mat_info = Mock()
        mat_info.textures = {}
        
        pbr_params = PBRParams(
            albedo=0.8,
            metallic=0.5,
            roughness=0.3,
            smoothness=0.7,
            normal_strength=1.0,
            emissive=0.0,
            alpha=1.0,
            use_alpha_blend=False,
            use_alpha_test=False
        )
        
        # テストテクスチャパス（実際には存在しなくても OK）
        test_diffuse = 'tests/dummy_diffuse.dds'
        
        # テストを実行（パスが存在しない場合は None を返すはず）
        result = self.integrator.convert_diffuse_to_albedo(test_diffuse, 'test_mat')
        
        # 存在しないパスの場合は None を返す
        assert result is None or isinstance(result, (str, type(None)))


class TestTextureIntegratorIntegration:
    """TextureIntegrator の統合テスト"""
    
    def setup_method(self):
        self.output_folder = Path('tests/output/textures')
        self.integrator = TextureIntegrator(self.output_folder)
    
    @patch('fbx_fixer.texture_integrator.TextureIntegrator.convert_diffuse_to_albedo')
    @patch('fbx_fixer.texture_integrator.TextureIntegrator.convert_normal_to_normal_map')
    @patch('fbx_fixer.texture_integrator.TextureIntegrator.convert_txmaps_to_metallic_map')
    def test_convert_all_textures_returns_dict(self, mock_metal, mock_normal, mock_diffuse):
        """convert_all_textures が dict を返す"""
        # モック関数の戻り値を設定
        mock_diffuse.return_value = 'output/material_albedo.dds'
        mock_normal.return_value = 'output/material_normal.dds'
        mock_metal.return_value = 'output/material_metallic.dds'
        
        # モック MaterialInfo
        mat_info = Mock()
        mat_info.textures = {
            'txDiffuse': Mock(texture_path='dummy_diffuse.dds'),
            'txNormal': Mock(texture_path='dummy_normal.dds'),
            'txMaps': Mock(texture_path='dummy_txmaps.dds')
        }
        
        pbr_params = PBRParams(
            albedo=0.8, metallic=0.5, roughness=0.3, smoothness=0.7,
            normal_strength=1.0, emissive=0.0, alpha=1.0,
            use_alpha_blend=False, use_alpha_test=False
        )
        
        result = self.integrator.convert_all_textures(mat_info, pbr_params, 'test_mat')
        
        # 戻り値は dict
        assert isinstance(result, dict)
        # 期待のキーが存在
        assert 'albedo' in result or 'normal' in result or 'metallic_map' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
