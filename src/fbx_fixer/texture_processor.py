"""
Texture Combining and Processing Module

Handles texture detection, mapping, and combination for PBR materials.
Supports combining multiple texture sources into combined textures
(e.g., Rough+Metal+AO into a single texture).

Based on AssettoCorsaSim shader documentation:
docs/Assetto Corsa Shaders, Texture maps list.txt
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, List, Set
import re

sys.path.append(os.path.curdir)

# ============================================================================
# SHADER-TEXTURE MAPPING DATABASE
# Based on docs/Assetto Corsa Shaders, Texture maps list.txt
# ============================================================================
SHADER_TEXTURE_REQUIREMENTS = {
    # Ground shaders
    'ksIdealLine': ['txDiffuse'],
    'ksSkidMark': ['txDiffuse'],

    # Object shaders
    'ksGrass': ['txDiffuse', 'txVariation'],
    'ksFlags': ['txDiffuse'],
    'ksTree': ['txDiffuse'],

    # Sky / Air shaders
    'ksSky': [],
    'ksSkyBox': [],
    'ksSkyCubemap': [],
    'ksClouds': ['txDiffuse'],
    'ksPostFOG': ['txDiffuse', 'txDepth'],

    # Car shaders
    'ksBrakeDisc': ['txDiffuse', 'txNormal', 'txGlow', 'txBlur', 'txNormalBlur'],
    'ksBrokenGlass': ['txDiffuse', 'txNormal'],
    'ksCarPaintSimple': ['txDiffuse'],
    'ksTyres': ['txDiffuse', 'txNormal', 'txDirty', 'txBlur', 'txNormalBlur'],
    'ksWindscreen': ['txDiffuse'],
    'newStefano_ksTyres': ['txDiffuse', 'txNormal'],
    'ksFakeCarShadows': ['txDiffuse'],
    'ksFakeCarShadowsGen': [],
    'ksCircularRPM': ['txDiffuse', 'txDiffuseON'],

    # Multiple use shaders
    'ksPerPixel': ['txDiffuse'],
    'ksPerPixel_dual_layer': ['txDiffuse', 'txLayer1', 'txLayer1_Mask'],
    'ksPerPixel_nosdw': ['txDiffuse'],
    'ksPerPixelAlpha': ['txDiffuse'],
    'ksPerPixelAT': ['txDiffuse'],
    'ksPerPixelAT_NM': ['txDiffuse', 'txNormal'],
    'ksPerPixelAT_NS': ['txDiffuse'],
    'ksPerPixelMultiMap': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail'],
    'ksPerPixelMultiMap_AT': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail'],
    'ksPerPixelMultiMap_AT_NMDetail': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail', 'txNormalDetail'],
    'ksPerPixelMultiMap_damage': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail', 'txDamage'],
    'ksPerPixelMultiMap_damage_dirt': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail', 'txDamage', 'txDust', 'txDamageMask'],
    'ksPerPixelMultiMap_NMDetail': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail', 'txNormalDetail'],
    'ksPerPixelMultiMapSimpleRefl': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail'],
    'ksPerPixelNM': ['txDiffuse', 'txNormal'],
    'ksPerPixelNM_UV2': ['txDiffuse', 'txNormal'],
    'ksPerPixelNM_UVMult': ['txDiffuse', 'txNormal'],
    'ksPerPixelReflection': ['txDiffuse'],
    'ksPerPixelSimpleRefl': ['txDiffuse'],
    'ksMultilayer': ['txDiffuse', 'txMask', 'txDetailR', 'txDetailG', 'txDetailB', 'txDetailA'],
    'ksMultilayer_fresnel_nm': ['txDiffuse', 'txMask', 'txDetailR', 'txDetailG', 'txDetailB', 'txDetailA', 'txDetailNM'],
    'ksMultilayer_objsp': ['txDiffuse', 'txMask', 'txDetailR', 'txDetailG', 'txDetailB', 'txDetailA'],

    # Other / Misc shaders
    'GL': [],
    'GL2D': [],
    'ksColourShader': [],
    'ksMegaShader': ['txDiffuse'],
    'ksMSDepthResolve': ['txDepth'],
    'ksOrenNayar': ['txDiffuse'],
    'ksOculusVR': [],
    'ksOculusVR2': [],
    'ksPostFOG_MS': ['txDiffuse', 'txDepth'],
    'ksShadowGen_debug': [],
    'ksSimpleShader': ['txDiffuse'],
    'ksSkinnedMesh': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail'],
    'ksSkinnedMesh_NMDetaill': ['txDiffuse', 'txNormal', 'txMaps', 'txDetail', 'txNormalDetail'],
    'ksTest': [],
    'ksYebisBlur': ['txBlurredDepth', 'txFinalDepth'],
    'ksYebisBlur_MS': ['txBlurredDepth', 'txFinalDepth'],
    'ksYebisPreDof': ['txDiffuse', 'txDepth'],

    # Disabled / editor-disabled shaders (keep entries for reference)
    'GLTextured': ['txDiffuse'],
    'ksCameraDirt': ['txDiffuse'],
    'ksFont': ['txDiffuse'],
    'ksFXAA': ['txCurrent'],
    'ksFXAA_0': ['txCurrent'],
    'ksFXAA_1': ['txCurrent'],
    'ksFXAA_2': ['txCurrent'],
    'ksFXAA_3': ['txCurrent'],
    'ksFXAA_4': ['txCurrent'],
    'ksFXAA_5': ['txCurrent'],
    'ksHighPass': ['txDiffuse', 'txDownsampled'],
    'ksParticle': ['txDiffuse'],
    'ksPostAdaptLum': ['txDiffuse', 'txNewLuma'],
    'ksPostBlur': ['txDepth', 'txSrc'],
    'ksPostBlur_MS': ['txDepth', 'txSrc'],
    'ksPostBlurH': ['txDiffuse'],
    'ksPostBlurRadial': ['txDepth', 'txSrc'],
    'ksPostBlurRadialMS': ['txDepth', 'txSrc'],
    'ksPostBlurV': ['txDiffuse'],
    'ksPostBW': ['txCurrent'],
    'ksPostCopy': ['txDiffuse'],
    'ksPostCopyLuma': ['txDiffuse'],
    'ksPostToneMap': ['txDiffuse', 'txBloom', 'txDownsampled'],
    'ksSelectedMesh': [],
    'ksShadowGen': ['txDiffuse'],
    'ksShadowGenAT': ['txDiffuse'],
    'ksShadowGenSKIN': ['txDiffuse'],
}


@dataclass
class ShaderProfile:
    """Profile of a shader with its required textures and characteristics"""
    shader_name: str
    category: str  # 'ground', 'object', 'sky', 'car', 'multiple_use', 'other'
    required_textures: List[str]
    has_normal_map: bool
    has_detail_map: bool
    has_damage_map: bool
    has_glow_map: bool
    has_reflection: bool
    # Alpha-channel related behaviour (from docs/About Alpha-channel.txt)
    uses_diffuse_alpha: bool = False
    uses_normal_alpha: bool = False
    uses_detail_alpha_affects_specular: bool = False
    uses_alpha_test: bool = False
    uses_diffuse_alpha_as_specular: bool = False


@dataclass
class TextureMapping:
    """Texture mapping information for a material"""
    material_name: str
    shader_name: str
    # Base textures (from INI)
    diffuse_texture: Optional[str] = None
    normal_texture: Optional[str] = None
    specular_texture: Optional[str] = None
    # Shader-specific textures
    maps_texture: Optional[str] = None  # txMaps (roughness/metallic/AO)
    detail_texture: Optional[str] = None  # txDetail
    damage_texture: Optional[str] = None  # txDamage
    dust_texture: Optional[str] = None  # txDust
    glow_texture: Optional[str] = None  # txGlow
    # Derived textures (to be generated/combined)
    roughness_texture: Optional[str] = None
    metallic_texture: Optional[str] = None
    emissive_texture: Optional[str] = None
    ao_texture: Optional[str] = None
    # Combined textures (for efficiency)
    pbr_combined_texture: Optional[str] = None  # Roughness + Metallic + AO


class ShaderProfiler:
    """Generate shader profile based on shader name using SHADER_TEXTURE_REQUIREMENTS database"""
    
    @staticmethod
    def get_shader_category(shader_name: str) -> str:
        """Determine shader category from shader name"""
        shader_lower = shader_name.lower()
        
        if 'ideal' in shader_lower or 'skid' in shader_lower:
            return 'ground'
        elif any(x in shader_lower for x in ['grass', 'flags', 'tree']):
            return 'object'
        elif any(x in shader_lower for x in ['sky', 'cloud', 'fog']):
            return 'sky'
        elif any(x in shader_lower for x in ['brake', 'tire', 'tyre', 'glass', 'paint', 'windscreen']):
            return 'car'
        elif 'perpixel' in shader_lower or 'multilayer' in shader_lower:
            return 'multiple_use'
        else:
            return 'other'
    
    @staticmethod
    def create_profile(shader_name: str) -> ShaderProfile:
        """
        Create a shader profile based on shader name
        
        Args:
            shader_name: Shader name from INI file
            
        Returns:
            ShaderProfile object
        """
        category = ShaderProfiler.get_shader_category(shader_name)
        
        # Get required textures from database
        required_textures = SHADER_TEXTURE_REQUIREMENTS.get(shader_name, [])
        
        # Analyze texture requirements
        required_set = set(required_textures)

        # Alpha / transparency behaviour inferred from docs
        shader_lower = shader_name.lower()

        uses_diffuse_alpha = False
        uses_normal_alpha = False
        uses_detail_alpha_affects_specular = False
        uses_alpha_test = False
        uses_diffuse_alpha_as_specular = False

        # MultiMap shaders: txDiffuse alpha marks where txDetail applies; txDetail alpha influences specular size
        if 'multimap' in shader_lower:
            uses_diffuse_alpha = True
            uses_detail_alpha_affects_specular = True

        # NM variants: normal alpha is used instead of diffuse alpha for masks/colorizing
        if 'nm' in shader_lower and 'perpixel' in shader_lower:
            uses_normal_alpha = True
            # NM shaders typically ignore diffuse alpha for transparency
            uses_diffuse_alpha = False

        # Per-pixel alpha / AT variants: alpha test or alpha-blend behaviour
        if 'perpixelat' in shader_lower or 'perpixelat_' in shader_lower:
            uses_alpha_test = True
            uses_diffuse_alpha = True
        elif 'perpixelalpha' in shader_lower or 'perpixelalpha' in shader_lower:
            uses_diffuse_alpha = True
        elif 'perpixel' in shader_lower and not uses_diffuse_alpha and not uses_normal_alpha:
            # most ksPerPixel family use txDiffuse alpha for transparency by default
            uses_diffuse_alpha = True

        # Tyres and brake discs: diffuse alpha used as specular/reflection level
        if any(x in shader_lower for x in ['kstyre', 'kstyres', 'ksbrakedisc', 'brakedisc']):
            uses_diffuse_alpha_as_specular = True

        profile = ShaderProfile(
            shader_name=shader_name,
            category=category,
            required_textures=required_textures,
            has_normal_map='txNormal' in required_set or 'txNormalDetail' in required_set or 'txNormalBlur' in required_set,
            has_detail_map='txDetail' in required_set or 'txDetailNM' in required_set or 'txDetailR' in required_set,
            has_damage_map='txDamage' in required_set,
            has_glow_map='txGlow' in required_set,
            has_reflection='Refl' in shader_name or 'refl' in shader_name.lower(),
            uses_diffuse_alpha=uses_diffuse_alpha,
            uses_normal_alpha=uses_normal_alpha,
            uses_detail_alpha_affects_specular=uses_detail_alpha_affects_specular,
            uses_alpha_test=uses_alpha_test,
            uses_diffuse_alpha_as_specular=uses_diffuse_alpha_as_specular,
        )
        
        return profile


class TextureDetector:
    """Detects and classifies textures in material definitions"""

    # Common texture naming patterns
    DIFFUSE_PATTERNS = [r'.*[Dd]iffuse.*', r'.*[Cc]olor.*', r'.*_D$', r'.*_d$']
    NORMAL_PATTERNS = [r'.*[Nn]ormal.*', r'.*NM.*', r'.*_N$', r'.*_n$']
    SPECULAR_PATTERNS = [r'.*[Ss]pecular.*', r'.*[Ss]pec.*', r'.*_S$', r'.*_s$']
    ROUGHNESS_PATTERNS = [r'.*[Rr]ough.*', r'.*[Rr]oughness.*']
    METALLIC_PATTERNS = [r'.*[Mm]etal.*', r'.*[Mm]etallic.*']
    EMISSIVE_PATTERNS = [r'.*[Ee]missive.*', r'.*[Ee]miss.*']
    AO_PATTERNS = [r'.*[Aa]mbient[Oo]cclusion.*', r'.*[Aa]mbient.*', r'.*AO.*', r'.*_A$', r'.*_a$']

    @staticmethod
    def _matches_patterns(name: str, patterns: List[str]) -> bool:
        """Check if name matches any of the patterns"""
        for pattern in patterns:
            if re.match(pattern, name):
                return True
        return False

    @classmethod
    def detect_texture_type(cls, texture_name: str) -> Optional[str]:
        """
        Detect texture type from filename.

        Args:
            texture_name: Texture filename or resource name

        Returns:
            Type string: 'diffuse', 'normal', 'specular', 'roughness', 'metallic', 'emissive', 'ao', or None
        """
        if cls._matches_patterns(texture_name, cls.DIFFUSE_PATTERNS):
            return 'diffuse'
        elif cls._matches_patterns(texture_name, cls.NORMAL_PATTERNS):
            return 'normal'
        elif cls._matches_patterns(texture_name, cls.SPECULAR_PATTERNS):
            return 'specular'
        elif cls._matches_patterns(texture_name, cls.ROUGHNESS_PATTERNS):
            return 'roughness'
        elif cls._matches_patterns(texture_name, cls.METALLIC_PATTERNS):
            return 'metallic'
        elif cls._matches_patterns(texture_name, cls.EMISSIVE_PATTERNS):
            return 'emissive'
        elif cls._matches_patterns(texture_name, cls.AO_PATTERNS):
            return 'ao'
        return None

    @classmethod
    def build_texture_mapping(cls, material_name: str, shader_name: str, textures: Dict[str, str]) -> TextureMapping:
        """
        Build texture mapping from raw texture dictionary using shader information.
        
        Args:
            material_name: Material name
            shader_name: Shader name (from INI)
            textures: Dictionary of texture names -> paths from INI
            
        Returns:
            TextureMapping object
        """
        mapping = TextureMapping(material_name=material_name, shader_name=shader_name)
        
        # Get expected textures for this shader
        expected_textures = SHADER_TEXTURE_REQUIREMENTS.get(shader_name, [])
        expected_set = set(expected_textures)

        # Map provided textures to expected slots
        for tex_name, tex_path in textures.items():
            # First try exact match with shader requirements
            if tex_name in expected_set:
                if tex_name == 'txDiffuse':
                    mapping.diffuse_texture = tex_path
                elif tex_name == 'txNormal':
                    mapping.normal_texture = tex_path
                elif tex_name == 'txMaps':
                    mapping.maps_texture = tex_path
                elif tex_name == 'txDetail':
                    mapping.detail_texture = tex_path
                elif tex_name == 'txDamage':
                    mapping.damage_texture = tex_path
                elif tex_name == 'txDust':
                    mapping.dust_texture = tex_path
                elif tex_name == 'txGlow':
                    mapping.glow_texture = tex_path
            else:
                # Fallback: pattern matching for unknown textures
                tex_type = cls.detect_texture_type(tex_name)
                if tex_type == 'diffuse':
                    if mapping.diffuse_texture is None:
                        mapping.diffuse_texture = tex_path
                elif tex_type == 'normal':
                    if mapping.normal_texture is None:
                        mapping.normal_texture = tex_path
                elif tex_type == 'specular':
                    mapping.specular_texture = tex_path
                elif tex_type == 'roughness':
                    mapping.roughness_texture = tex_path
                elif tex_type == 'metallic':
                    mapping.metallic_texture = tex_path
                elif tex_type == 'emissive':
                    mapping.emissive_texture = tex_path
                elif tex_type == 'ao':
                    mapping.ao_texture = tex_path

        return mapping
    
    # Legacy method for backward compatibility
    @classmethod
    def build_texture_mapping_legacy(cls, material_name: str, textures: Dict[str, str]) -> TextureMapping:
        """
        Build texture mapping from raw texture dictionary (pattern matching only).
        This is the legacy version without shader information.
        
        Args:
            material_name: Material name
            textures: Dictionary of texture names -> paths from INI
            
        Returns:
            TextureMapping object
        """
        # Use empty shader name for legacy compatibility
        return cls.build_texture_mapping(material_name, 'unknown', textures)


class TextureProcessor:
    """
    Processes and combines textures for PBR materials.
    
    Integrates shader information, texture detection, and planning.
    
    Note: Actual texture manipulation (combining, resizing, etc.)
    is deferred to the FBX integration layer which may use
    ezTexConv or other tools.
    """

    def __init__(self):
        """Initialize the texture processor"""
        self.detector = TextureDetector()
        self.profiler = ShaderProfiler()

    def generate_texture_requirements(
        self,
        mapping: TextureMapping,
        profile: ShaderProfile
    ) -> Dict[str, List[str]]:
        """
        Generate texture processing requirements based on mapping and profile.

        Args:
            mapping: TextureMapping object
            profile: ShaderProfile object

        Returns:
            Dictionary of processing operations required
        """
        requirements = {}
        
        # Check for missing required textures
        missing = []
        for required_tex in profile.required_textures:
            if required_tex == 'txDiffuse' and mapping.diffuse_texture is None:
                missing.append('txDiffuse')
            elif required_tex == 'txNormal' and mapping.normal_texture is None:
                missing.append('txNormal')
            elif required_tex == 'txMaps' and mapping.maps_texture is None:
                missing.append('txMaps')
            elif required_tex == 'txDetail' and mapping.detail_texture is None:
                missing.append('txDetail')
        
        if missing:
            requirements['missing_textures'] = missing
        
        # Check if we need to combine PBR textures
        sources = []
        if mapping.maps_texture:  # txMaps typically contains roughness/metallic/AO
            sources.append('maps')
        if mapping.roughness_texture:
            sources.append('roughness')
        if mapping.metallic_texture:
            sources.append('metallic')
        if mapping.ao_texture:
            sources.append('ao')
        
        if len(sources) > 1:
            requirements['combine_pbr'] = sources
            mapping.pbr_combined_texture = f"{mapping.material_name}_PBR_combined.dds"

        # Check normal map processing
        if mapping.normal_texture and profile.has_normal_map:
            requirements['process_normal'] = [mapping.normal_texture]
        
        # Check damage/detail map processing
        if mapping.damage_texture and profile.has_damage_map:
            requirements['process_damage'] = [mapping.damage_texture]
        if mapping.detail_texture and profile.has_detail_map:
            requirements['process_detail'] = [mapping.detail_texture]
        
        # Check glow map processing
        if mapping.glow_texture and profile.has_glow_map:
            requirements['process_glow'] = [mapping.glow_texture]

        return requirements

    def plan_texture_operations(
        self,
        material_name: str,
        shader_name: str,
        textures: Dict[str, str]
    ) -> Dict:
        """
        Plan all texture operations for a material.

        Args:
            material_name: Material name
            shader_name: Shader name
            textures: Raw texture dictionary from INI

        Returns:
            Dictionary containing:
            - material_name: Material name
            - shader_name: Shader name
            - mapping: TextureMapping object
            - profile: ShaderProfile object
            - operations: Dictionary of required operations
        """
        # Create shader profile
        profile = self.profiler.create_profile(shader_name)
        
        # Build texture mapping using shader information
        mapping = self.detector.build_texture_mapping(material_name, shader_name, textures)
        
        # Generate processing requirements
        operations = self.generate_texture_requirements(mapping, profile)

        return {
            'material_name': material_name,
            'shader_name': shader_name,
            'mapping': mapping,
            'profile': profile,
            'operations': operations
        }


if __name__ == "__main__":
    # Example usage
    detector = TextureDetector()
    profiler = ShaderProfiler()
    processor = TextureProcessor()

    print("=" * 70)
    print("Example 1: Shader Profile Test")
    print("=" * 70)
    
    shader_name = "ksPerPixelMultiMap_damage_dirt"
    profile = profiler.create_profile(shader_name)
    print(f"Shader: {shader_name}")
    print(f"  Category: {profile.category}")
    print(f"  Has Normal: {profile.has_normal_map}")
    print(f"  Has Detail: {profile.has_detail_map}")
    print(f"  Has Damage: {profile.has_damage_map}")
    print(f"  Required Textures: {profile.required_textures}")

    print("\n" + "=" * 70)
    print("Example 2: Texture Mapping with Shader")
    print("=" * 70)
    
    example_textures = {
        'txDiffuse': 'CAR_black_D.dds',
        'txNormal': 'CAR_black_NM.dds',
        'txMaps': 'CAR_black_MAPS.dds',
        'txDetail': 'detail.dds',
        'txDamage': 'damage.dds',
        'txDust': 'dust.dds',
        'txDamageMask': 'damage_mask.dds',
    }
    
    mapping = detector.build_texture_mapping("Dark_Plastic", shader_name, example_textures)
    print(f"Material: {mapping.material_name}")
    print(f"Shader: {mapping.shader_name}")
    print(f"  Diffuse: {mapping.diffuse_texture}")
    print(f"  Normal: {mapping.normal_texture}")
    print(f"  Maps: {mapping.maps_texture}")
    print(f"  Detail: {mapping.detail_texture}")
    print(f"  Damage: {mapping.damage_texture}")

    print("\n" + "=" * 70)
    print("Example 3: Full Texture Operation Planning")
    print("=" * 70)

    plan = processor.plan_texture_operations("Dark_Plastic", shader_name, example_textures)
    print(f"Material: {plan['material_name']}")
    print(f"Shader: {plan['shader_name']}")
    print(f"Category: {plan['profile'].category}")
    print(f"Required Textures Count: {len(plan['profile'].required_textures)}")
    print(f"Operations: {plan['operations']}")
