"""
Smoothness計算のユニットテスト

texture_integrator と pbr_converter の Smoothness 計算をテストします。
"""

import pytest
from pathlib import Path
import sys
src = Path(__file__).parent.parent / 'src'
sys.path.append(str(src))


from src.fbx_fixer.pbr_converter import (
    BlinnPhongToPBRConverter,
    BlinnPhongParams,
    PBRParams
)


class TestSmoothnessCalculation:
    """Smoothness 計算のテストケース"""
    
    def setup_method(self):
        """各テストの前に実行"""
        self.converter = BlinnPhongToPBRConverter()
    
    def test_calculate_smoothness_from_roughness_zero(self):
        """Roughness = 0 のときは Smoothness = 1"""
        smoothness = self.converter.calculate_smoothness_from_roughness(0.0)
        assert smoothness == 1.0
    
    def test_calculate_smoothness_from_roughness_one(self):
        """Roughness = 1 のときは Smoothness = 0"""
        smoothness = self.converter.calculate_smoothness_from_roughness(1.0)
        assert smoothness == 0.0
    
    def test_calculate_smoothness_from_roughness_half(self):
        """Roughness = 0.5 のときは Smoothness = 0.5"""
        smoothness = self.converter.calculate_smoothness_from_roughness(0.5)
        assert smoothness == 0.5
    
    def test_calculate_smoothness_from_roughness_clamped(self):
        """Roughness > 1 や < 0 の場合はクリップされる"""
        # クリップはmax(0, min(1, value))で実装されている
        # Roughness = -0.5 → Smoothness = 1 - (-0.5) = 1.5 → clipped to 1.0
        smoothness_neg = self.converter.calculate_smoothness_from_roughness(-0.5)
        assert smoothness_neg == 1.0  # Clipped to max value
        
        # Roughness = 1.5 → Smoothness = 1 - 1.5 = -0.5 → clipped to 0.0
        smoothness_over = self.converter.calculate_smoothness_from_roughness(1.5)
        assert smoothness_over == 0.0  # Clipped to min value
    
    def test_pbr_params_contains_smoothness(self):
        """PBRParams に smoothness フィールドが存在"""
        bp = BlinnPhongParams(
            shader="test_shader",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=50.0,
            ks_emissive=0.0,
            ks_alpha_ref=0.0
        )
        pbr = self.converter.convert(bp)
        
        assert hasattr(pbr, 'smoothness')
        assert isinstance(pbr.smoothness, float)
        assert 0.0 <= pbr.smoothness <= 1.0
    
    def test_smoothness_is_inverse_of_roughness(self):
        """Smoothness = 1 - Roughness"""
        bp = BlinnPhongParams(
            shader="test_shader",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=50.0,
            ks_emissive=0.0,
            ks_alpha_ref=0.0
        )
        pbr = self.converter.convert(bp)
        
        # smoothness + roughness ≈ 1.0
        assert abs((pbr.smoothness + pbr.roughness) - 1.0) < 0.01
    
    def test_high_specular_exp_gives_high_smoothness(self):
        """高いksSpecularExp → 低いRoughness → 高いSmoothness"""
        # ksSpecularExp が大きい (鋭いハイライト)
        bp_high = BlinnPhongParams(
            shader="test_shader",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=255.0,  # 高い
            ks_emissive=0.0,
            ks_alpha_ref=0.0
        )
        pbr_high = self.converter.convert(bp_high)
        
        # ksSpecularExp が小さい (ぼやけたハイライト)
        bp_low = BlinnPhongParams(
            shader="test_shader",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=2.0,  # 低い
            ks_emissive=0.0,
            ks_alpha_ref=0.0
        )
        pbr_low = self.converter.convert(bp_low)
        
        # 高いExp → 高いSmoothness
        assert pbr_high.smoothness > pbr_low.smoothness


class TestPBRParamsIntegrity:
    """PBRParams オブジェクト全体の整合性テスト"""
    
    def setup_method(self):
        self.converter = BlinnPhongToPBRConverter()
    
    def test_pbr_params_all_fields_present(self):
        """PBRParams に全フィールドが存在"""
        bp = BlinnPhongParams(
            shader="test",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=50.0,
            ks_emissive=0.1,
            ks_alpha_ref=0.5
        )
        pbr = self.converter.convert(bp)
        
        required_fields = [
            'albedo', 'metallic', 'roughness', 'smoothness',
            'normal_strength', 'emissive', 'alpha',
            'use_alpha_blend', 'use_alpha_test'
        ]
        for field in required_fields:
            assert hasattr(pbr, field), f"Missing field: {field}"
    
    def test_pbr_params_in_valid_ranges(self):
        """PBRParams 全値が有効な範囲内"""
        bp = BlinnPhongParams(
            shader="test",
            ks_ambient=0.3,
            ks_diffuse=0.8,
            ks_specular=0.5,
            ks_specular_exp=50.0,
            ks_emissive=0.1,
            ks_alpha_ref=0.5
        )
        pbr = self.converter.convert(bp)
        
        float_fields = ['albedo', 'metallic', 'roughness', 'smoothness',
                        'normal_strength', 'emissive', 'alpha']
        for field in float_fields:
            value = getattr(pbr, field)
            assert 0.0 <= value <= 1.0, f"{field}={value} is out of range [0, 1]"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
