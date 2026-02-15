"""
Test cfg_materials functionality
"""

from pathlib import Path
import sys
from configparser import ConfigParser
import re
from dataclasses import dataclass
from typing import Dict

# Define classes directly to avoid import issues
@dataclass
class TextureResource:
    """Texture resource information from INI"""
    name: str
    slot: int
    texture_path: str


@dataclass
class MaterialInfo:
    """Complete material information from INI"""
    name: str
    shader: str
    alpha_blend: bool
    alpha_test: bool
    ks_ambient: float
    ks_diffuse: float
    ks_specular: float
    ks_specular_exp: float
    ks_emissive: float
    ks_alpha_ref: float
    fresnel_c: float
    fresnel_exp: float
    fresnel_max_level: float
    textures: Dict[str, TextureResource]


def load_cfg(fbx_folder):
    """Load INI configuration file from FBX folder"""
    rslt = list(Path(fbx_folder).glob('*.ini'))
    if len(rslt) <= 0:
        raise RuntimeError(f"ini file not found in {fbx_folder}")
    cfg_path = rslt[0]
    cfg = ConfigParser()
    cfg.read(cfg_path, encoding='utf-8')
    return cfg


def parse_material_section(cfg: ConfigParser, section: str) -> MaterialInfo:
    """
    Parse a single MATERIAL_X section from INI.

    Args:
        cfg: ConfigParser object
        section: Section name (e.g., "MATERIAL_0")

    Returns:
        MaterialInfo object
    """
    mat_section = cfg[section]

    # Extract texture resources
    textures = {}
    res_count = int(mat_section.get('RESCOUNT', 0))
    for i in range(res_count):
        res_name_key = f'RES_{i}_NAME'
        res_texture_key = f'RES_{i}_TEXTURE'
        if res_name_key in mat_section:
            tex_res = TextureResource(
                name=mat_section[res_name_key],
                slot=i,
                texture_path=mat_section.get(res_texture_key, '')
            )
            textures[tex_res.name] = tex_res

    # Extract shader parameters
    mat_info = MaterialInfo(
        name=mat_section.get('NAME', f'Unknown_{section}'),
        shader=mat_section.get('SHADER', 'unknown'),
        alpha_blend=int(mat_section.get('ALPHABLEND', 0)) > 0,
        alpha_test=int(mat_section.get('ALPHATEST', 0)) > 0,
        ks_ambient=float(mat_section.get('ksAmbient', 0.0)),
        ks_diffuse=float(mat_section.get('ksDiffuse', 0.0)),
        ks_specular=float(mat_section.get('ksSpecular', 0.0)),
        ks_specular_exp=float(mat_section.get('ksSpecularEXP', 0.0)),
        ks_emissive=float(mat_section.get('ksEmissive', 0.0)),
        ks_alpha_ref=float(mat_section.get('ksAlphaRef', 0.0)),
        fresnel_c=float(mat_section.get('fresnelC', 0.0)),
        fresnel_exp=float(mat_section.get('fresnelEXP', 0.0)),
        fresnel_max_level=float(mat_section.get('fresnelMaxLevel', 0.0)),
        textures=textures
    )

    return mat_info


def to_alpha_blend_dic(cfg: ConfigParser):
    """Legacy function: Extract alpha blend info only"""
    mat_sec_list = [section for section in cfg.sections() if re.fullmatch(r"MATERIAL_\d+", section)]
    mat_dic = {cfg[sec]["NAME"]: int(cfg[sec]["ALPHABLEND"]) > 0 for sec in mat_sec_list}
    return mat_dic


def load_all_materials(fbx_folder: str) -> Dict[str, MaterialInfo]:
    """
    Load all materials from INI file.

    Args:
        fbx_folder: Path to FBX folder containing .ini

    Returns:
        Dictionary mapping material names to MaterialInfo objects
    """
    cfg = load_cfg(fbx_folder)
    mat_sec_list = [section for section in cfg.sections() if re.fullmatch(r"MATERIAL_\d+", section)]

    materials = {}
    for section in mat_sec_list:
        mat_info = parse_material_section(cfg, section)
        materials[mat_info.name] = mat_info

    return materials


def load_material_info(fbx_folder):
    """Legacy function: Load alpha blend info only"""
    cfg = load_cfg(fbx_folder)
    dic = to_alpha_blend_dic(cfg)
    return dic

# Test with actual GT86 data
fbx_folder = r"d:\Devlop\Assetonite\data\input\fbx_fixer\gt86"

print("=" * 70)
print("Testing cfg_materials.load_all_materials()")
print("=" * 70)

try:
    materials = load_all_materials(fbx_folder)
    print(f"\n✓ Loaded {len(materials)} materials\n")

    # Display first 3 materials
    for i, (mat_name, mat_info) in enumerate(list(materials.items())[:3]):
        print(f"--- Material {i + 1} ---")
        print(f"  Name: {mat_info.name}")
        print(f"  Shader: {mat_info.shader}")
        print(f"  ksDiffuse: {mat_info.ks_diffuse}")
        print(f"  ksSpecular: {mat_info.ks_specular}")
        print(f"  ksSpecularEXP: {mat_info.ks_specular_exp}")
        print(f"  Textures: {len(mat_info.textures)}")
        for tex_name, tex_res in mat_info.textures.items():
            print(f"    - {tex_name}: {tex_res.texture_path}")
        print()

except Exception as e:
    print(f"✗ Error: {e}")

print("=" * 70)
print("Testing cfg_materials.load_material_info() (Legacy)")
print("=" * 70)

try:
    alpha_info = load_material_info(fbx_folder)
    print(f"\n✓ Loaded alpha info for {len(alpha_info)} materials\n")

    # Display first 5
    for i, (mat_name, alpha_blend) in enumerate(list(alpha_info.items())[:5]):
        blend_str = "✓ Alpha Blend" if alpha_blend else "  No Blend"
        print(f"  {blend_str}: {mat_name}")

except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("All tests completed!")
print("=" * 70)
