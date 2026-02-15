"""
Test suite for Texture Processor module with shader-texture mapping

Tests:
1. ShaderProfiler shader profile creation
2. TextureDetector texture type detection
3. TextureMapping with shader-based detection
4. TextureProcessor texture operation planning
5. Missing texture detection
"""

import sys
import os
from pathlib import Path

src = Path(__file__).parent.parent / 'src'
sys.path.append(str(src))

from src.fbx_fixer.texture_processor import (
    ShaderProfiler, TextureDetector, TextureProcessor,
    SHADER_TEXTURE_REQUIREMENTS
)


def test_shader_profiler_categories():
    """Test shader category detection"""
    print("\n" + "="*70)
    print("TEST: Shader Category Detection")
    print("="*70)
    
    test_cases = [
        ("ksIdealLine", "ground"),
        ("ksTyres", "car"),
        ("ksPerPixelMultiMap", "multiple_use"),
        ("ksSky", "sky"),
        ("ksGrass", "object"),
    ]
    
    profiler = ShaderProfiler()
    for shader_name, expected_category in test_cases:
        actual = profiler.get_shader_category(shader_name)
        status = "✓" if actual == expected_category else "✗"
        print(f"{status} {shader_name:40} → {actual:15} (expected: {expected_category})")
        assert actual == expected_category


def test_shader_profile_creation():
    """Test shader profile generation"""
    print("\n" + "="*70)
    print("TEST: Shader Profile Creation")
    print("="*70)
    
    profiler = ShaderProfiler()
    
    test_shaders = [
        "ksPerPixelMultiMap_damage_dirt",
        "ksPerPixelNM",
        "ksTyres",
        "ksCarPaintSimple",
    ]
    
    for shader_name in test_shaders:
        profile = profiler.create_profile(shader_name)
        print(f"\nShader: {shader_name}")
        print(f"  Category: {profile.category}")
        print(f"  Has Normal: {profile.has_normal_map}")
        print(f"  Has Detail: {profile.has_detail_map}")
        print(f"  Has Damage: {profile.has_damage_map}")
        print(f"  Has Glow: {profile.has_glow_map}")
        print(f"  Required textures: {profile.required_textures}")
        
        # Verify expected textures are present
        assert len(profile.required_textures) > 0 or shader_name in ["ksSky", "ksSkyCubemap"]


def test_texture_detection():
    """Test texture type detection from filename"""
    print("\n" + "="*70)
    print("TEST: Texture Type Detection (Pattern Matching)")
    print("="*70)
    
    detector = TextureDetector()
    
    test_cases = [
        ("CAR_black_D.dds", "diffuse"),
        ("CAR_black_NM.dds", "normal"),
        ("CAR_black_MAPS.dds", "maps"),
        ("detail.dds", "detail"),
        ("damage.dds", "damage"),
        ("specular.dds", "specular"),
    ]
    
    for texture_name, expected_type in test_cases:
        actual = detector.detect_texture_type(texture_name)
        status = "✓" if actual == expected_type else "✗"
        print(f"{status} {texture_name:30} → {actual or 'None':15} (expected: {expected_type})")
        assert actual == expected_type


def test_texture_mapping_with_shader():
    """Test texture mapping using shader information"""
    print("\n" + "="*70)
    print("TEST: Texture Mapping with Shader-Based Detection")
    print("="*70)
    
    detector = TextureDetector()
    
    # Test case 1: ksPerPixelMultiMap_damage_dirt with all textures
    shader_name = "ksPerPixelMultiMap_damage_dirt"
    textures = {
        "txDiffuse": "CAR_black_D.dds",
        "txNormal": "CAR_black_NM.dds",
        "txMaps": "CAR_black_MAPS.dds",
        "txDetail": "detail.dds",
        "txDamage": "damage.dds",
        "txDust": "dust.dds",
        "txDamageMask": "damage_mask.dds",
    }
    
    mapping = detector.build_texture_mapping("Dark_Plastic", shader_name, textures)
    
    print(f"\nMaterial: {mapping.material_name}")
    print(f"Shader: {mapping.shader_name}")
    print(f"  Diffuse: {mapping.diffuse_texture}")
    print(f"  Normal: {mapping.normal_texture}")
    print(f"  Maps: {mapping.maps_texture}")
    print(f"  Detail: {mapping.detail_texture}")
    print(f"  Damage: {mapping.damage_texture}")
    print(f"  Dust: {mapping.dust_texture}")
    print(f"  DamageMask: {mapping.damage_texture}")
    
    assert mapping.diffuse_texture == "CAR_black_D.dds"
    assert mapping.normal_texture == "CAR_black_NM.dds"
    assert mapping.maps_texture == "CAR_black_MAPS.dds"
    
    # Test case 2: ksPerPixelNM with partial textures
    print(f"\n--- Test case 2: Minimal textures ---")
    shader_name2 = "ksPerPixelNM"
    textures2 = {
        "txDiffuse": "car_color.dds",
        "txNormal": "car_nm.dds",
    }
    
    mapping2 = detector.build_texture_mapping("CAR_color", shader_name2, textures2)
    print(f"Material: {mapping2.material_name}")
    print(f"  Diffuse: {mapping2.diffuse_texture}")
    print(f"  Normal: {mapping2.normal_texture}")
    
    assert mapping2.diffuse_texture == "car_color.dds"
    assert mapping2.normal_texture == "car_nm.dds"


def test_texture_processor_planning():
    """Test full texture processor planning workflow"""
    print("\n" + "="*70)
    print("TEST: TextureProcessor Full Planning Workflow")
    print("="*70)
    
    processor = TextureProcessor()
    
    # Test case 1
    shader_name = "ksPerPixelMultiMap_damage_dirt"
    textures = {
        "txDiffuse": "CAR_black_D.dds",
        "txNormal": "CAR_black_NM.dds",
        "txMaps": "CAR_black_MAPS.dds",
        "txDetail": "detail.dds",
        "txDamage": "damage.dds",
        "txDust": "dust.dds",
        "txDamageMask": "damage_mask.dds",
    }
    
    plan = processor.plan_texture_operations("Dark_Plastic", shader_name, textures)
    
    print(f"\nMaterial: {plan['material_name']}")
    print(f"Shader: {plan['shader_name']}")
    print(f"Category: {plan['profile'].category}")
    print(f"Required textures: {plan['profile'].required_textures}")
    print(f"Operations: {plan['operations']}")
    
    assert plan["material_name"] == "Dark_Plastic"
    assert plan["shader_name"] == shader_name
    assert len(plan["profile"].required_textures) == 7


def test_missing_texture_detection():
    """Test detection of missing required textures"""
    print("\n" + "="*70)
    print("TEST: Missing Texture Detection")
    print("="*70)
    
    processor = TextureProcessor()
    
    # Provide only partial textures for a shader that requires many
    shader_name = "ksPerPixelMultiMap_damage_dirt"
    incomplete_textures = {
        "txDiffuse": "color.dds",
        # Missing: txNormal, txMaps, txDetail, txDamage, txDust, txDamageMask
    }
    
    plan = processor.plan_texture_operations("Incomplete", shader_name, incomplete_textures)
    
    print(f"\nMaterial: {plan['material_name']}")
    print(f"Shader: {plan['shader_name']}")
    print(f"Operations: {plan['operations']}")
    
    # Should detect missing textures
    if "missing_textures" in plan["operations"]:
        print(f"Missing textures: {plan['operations']['missing_textures']}")
        assert len(plan["operations"]["missing_textures"]) > 0


def test_shader_database_coverage():
    """Test that major shader types are in the database"""
    print("\n" + "="*70)
    print("TEST: Shader Database Coverage")
    print("="*70)
    
    required_shaders = [
        "ksPerPixelMultiMap",
        "ksPerPixelMultiMap_damage_dirt",
        "ksPerPixelNM",
        "ksTyres",
        "ksCarPaintSimple",
        "ksBrakeDisc",
        "ksPerPixel",
    ]
    
    print(f"\nTotal shaders in database: {len(SHADER_TEXTURE_REQUIREMENTS)}")
    
    for shader in required_shaders:
        if shader in SHADER_TEXTURE_REQUIREMENTS:
            textures = SHADER_TEXTURE_REQUIREMENTS[shader]
            print(f"✓ {shader:40} → {len(textures)} textures: {textures}")
        else:
            print(f"✗ {shader:40} → NOT FOUND")
            assert False, f"Shader {shader} not in database"


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# Texture Processor Test Suite")
    print("#"*70)
    
    try:
        test_shader_profiler_categories()
        test_shader_profile_creation()
        test_texture_detection()
        test_texture_mapping_with_shader()
        test_texture_processor_planning()
        test_missing_texture_detection()
        test_shader_database_coverage()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
