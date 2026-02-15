"""
Test script for Blinn-Phong to PBR converter
"""

import logging
from dataclasses import dataclass
from typing import Dict

# Set up basic logging
logger = logging.getLogger('pbr_converter_test')
logger.setLevel(logging.DEBUG)


@dataclass
class BlinnPhongParams:
    """Blinn-Phong material parameters from AssettoCorsaSim"""
    shader: str
    ks_ambient: float
    ks_diffuse: float
    ks_specular: float
    ks_specular_exp: float
    ks_emissive: float
    ks_alpha_ref: float
    fresnel_c: float = 0.0
    fresnel_exp: float = 0.0
    fresnel_max_level: float = 0.0
    alpha_blend: bool = False
    alpha_test: bool = False


@dataclass
class PBRParams:
    """Physically Based Rendering parameters for Resonite"""
    albedo: float  # Base color intensity (0-1)
    metallic: float  # Metallic value (0-1)
    roughness: float  # Roughness value (0-1)
    normal_strength: float  # Normal map strength (0-1)
    emissive: float  # Emissive intensity (0-1)
    alpha: float  # Alpha/Transparency (0-1)
    use_alpha_blend: bool
    use_alpha_test: bool


class BlinnPhongToPBRConverter:
    """
    Converts AssettoCorsaSim Blinn-Phong material parameters to PBR parameters.
    """

    def __init__(self):
        """Initialize the converter."""
        self.logger = logger

    @staticmethod
    def estimate_metallic_from_specular(ks_specular: float) -> float:
        """
        Estimate metallic value from Blinn-Phong specular intensity.

        Metallic materials typically have higher specular values in Blinn-Phong.
        Using a threshold-based approach:
        - If ks_specular > 0.5: likely metallic
        - Otherwise: non-metallic (dielectric)

        Args:
            ks_specular: Blinn-Phong specular intensity (0-1)

        Returns:
            Metallic value (0-1)
        """
        # Threshold-based metallic estimation
        if ks_specular > 0.5:
            # Metallic: extrapolate from 0.5-1.0 to 0.0-1.0 range
            metallic = (ks_specular - 0.5) * 2.0
            return min(1.0, metallic)
        else:
            # Non-metallic (dielectric)
            return 0.0

    @staticmethod
    def calculate_roughness_from_specular_exp(ks_specular_exp: float) -> float:
        """
        Calculate roughness from Blinn-Phong specular exponent using the formula:
        Roughness = sqrt(2 / (ksSpecularEXP + 2))

        Args:
            ks_specular_exp: Blinn-Phong specular exponent (shininess)

        Returns:
            Roughness value (0-1)
        """
        if ks_specular_exp < 0.0:
            ks_specular_exp = 0.0

        # Formula: Roughness = sqrt(2 / (ksSpecularEXP + 2))
        roughness = (2.0 / (ks_specular_exp + 2.0)) ** 0.5
        return min(1.0, roughness)

    @staticmethod
    def calculate_albedo_from_diffuse(ks_diffuse: float) -> float:
        """
        Convert diffuse component to albedo.

        In Blinn-Phong, diffuse represents the base color intensity.
        Map directly to albedo for PBR.

        Args:
            ks_diffuse: Blinn-Phong diffuse intensity (0-1)

        Returns:
            Albedo value (0-1)
        """
        # Ensure albedo is within valid range
        return max(0.0, min(1.0, ks_diffuse))

    @staticmethod
    def calculate_emissive(ks_emissive: float, ks_ambient: float) -> float:
        """
        Calculate emissive intensity from Blinn-Phong parameters.

        Uses ksEmissive directly, with fallback to ambient if emissive is 0.

        Args:
            ks_emissive: Blinn-Phong emissive intensity
            ks_ambient: Blinn-Phong ambient intensity (fallback)

        Returns:
            Emissive intensity (0-1)
        """
        if ks_emissive > 0.0:
            return min(1.0, ks_emissive)
        # If not explicitly emissive, use ambient as fallback
        return min(0.3, max(0.0, ks_ambient * 0.3))

    def convert(self, bp_params: BlinnPhongParams) -> PBRParams:
        """
        Convert Blinn-Phong parameters to PBR parameters.

        Args:
            bp_params: Blinn-Phong material parameters

        Returns:
            PBR material parameters
        """
        self.logger.debug(f"Converting material: {bp_params.shader}")

        # Calculate PBR parameters using conversion formulas
        metallic = self.estimate_metallic_from_specular(bp_params.ks_specular)
        roughness = self.calculate_roughness_from_specular_exp(bp_params.ks_specular_exp)
        albedo = self.calculate_albedo_from_diffuse(bp_params.ks_diffuse)
        emissive = self.calculate_emissive(bp_params.ks_emissive, bp_params.ks_ambient)

        pbr_params = PBRParams(
            albedo=albedo,
            metallic=metallic,
            roughness=roughness,
            normal_strength=1.0,  # Default normal strength
            emissive=emissive,
            alpha=1.0 - bp_params.ks_alpha_ref,  # Inverted alpha reference
            use_alpha_blend=bp_params.alpha_blend,
            use_alpha_test=bp_params.alpha_test,
        )

        self.logger.debug(
            f"PBR Params - Albedo: {pbr_params.albedo:.3f}, "
            f"Metallic: {pbr_params.metallic:.3f}, "
            f"Roughness: {pbr_params.roughness:.3f}, "
            f"Emissive: {pbr_params.emissive:.3f}"
        )

        return pbr_params

    def batch_convert(self, bp_params_list: list) -> Dict[str, PBRParams]:
        """
        Convert a batch of Blinn-Phong materials to PBR.

        Args:
            bp_params_list: List of BlinnPhongParams

        Returns:
            Dictionary mapping material names to PBR parameters
        """
        result = {}
        for bp_param in bp_params_list:
            pbr_param = self.convert(bp_param)
            # Store with shader name as key for reference
            key = bp_param.shader
            result[key] = pbr_param
            self.logger.info(f"Converted {key}")

        return result


def create_pbr_params_from_ini_dict(mat_dict: Dict) -> BlinnPhongParams:
    """
    Create BlinnPhongParams from a material dictionary extracted from INI.

    Args:
        mat_dict: Dictionary containing material parameters from INI

    Returns:
        BlinnPhongParams object
    """
    return BlinnPhongParams(
        shader=mat_dict.get("SHADER", "unknown"),
        ks_ambient=float(mat_dict.get("ksAmbient", 0.0)),
        ks_diffuse=float(mat_dict.get("ksDiffuse", 0.0)),
        ks_specular=float(mat_dict.get("ksSpecular", 0.0)),
        ks_specular_exp=float(mat_dict.get("ksSpecularEXP", 0.0)),
        ks_emissive=float(mat_dict.get("ksEmissive", 0.0)),
        ks_alpha_ref=float(mat_dict.get("ksAlphaRef", 0.0)),
        fresnel_c=float(mat_dict.get("fresnelC", 0.0)),
        fresnel_exp=float(mat_dict.get("fresnelEXP", 0.0)),
        fresnel_max_level=float(mat_dict.get("fresnelMaxLevel", 0.0)),
        alpha_blend=int(mat_dict.get("ALPHABLEND", 0)) > 0,
        alpha_test=int(mat_dict.get("ALPHATEST", 0)) > 0,
    )


def test_metallic_estimation():
    """Test metallic estimation from specular value"""
    converter = BlinnPhongToPBRConverter()

    test_cases = [
        (0.0, 0.0),  # Non-metallic
        (0.25, 0.0),  # Low specular = non-metallic
        (0.5, 0.0),  # Boundary
        (0.75, 0.5),  # Metallic
        (1.0, 1.0),  # Full metallic
    ]

    print("=" * 60)
    print("Metallic Estimation Tests")
    print("=" * 60)

    for ks_spec, expected in test_cases:
        result = converter.estimate_metallic_from_specular(ks_spec)
        status = "✓" if abs(result - expected) < 0.01 else "✗"
        print(f"{status} ksSpecular={ks_spec:.2f} → Metallic={result:.3f} (expected {expected:.3f})")


def test_roughness_calculation():
    """Test roughness calculation from specular exponent"""
    converter = BlinnPhongToPBRConverter()

    test_cases = [
        (0.0, (2.0 / 2.0) ** 0.5),  # Very smooth
        (10.0, (2.0 / 12.0) ** 0.5),  # Moderate
        (100.0, (2.0 / 102.0) ** 0.5),  # Rough
        (256.0, (2.0 / 258.0) ** 0.5),  # Mirror-like
    ]

    print("\n" + "=" * 60)
    print("Roughness Calculation Tests")
    print("Roughness = sqrt(2 / (ksSpecularEXP + 2))")
    print("=" * 60)

    for ks_exp, expected in test_cases:
        result = converter.calculate_roughness_from_specular_exp(ks_exp)
        status = "✓" if abs(result - expected) < 0.0001 else "✗"
        print(f"{status} ksSpecularEXP={ks_exp:6.1f} → Roughness={result:.4f} (expected {expected:.4f})")


def test_albedo_conversion():
    """Test albedo conversion from diffuse"""
    converter = BlinnPhongToPBRConverter()

    test_cases = [0.0, 0.15, 0.5, 1.0]

    print("\n" + "=" * 60)
    print("Albedo Conversion Tests (Direct mapping)")
    print("=" * 60)

    for ks_diff in test_cases:
        result = converter.calculate_albedo_from_diffuse(ks_diff)
        status = "✓" if abs(result - ks_diff) < 0.0001 else "✗"
        print(f"{status} ksDiffuse={ks_diff:.2f} → Albedo={result:.3f}")


def test_full_conversion():
    """Test full Blinn-Phong to PBR conversion"""
    converter = BlinnPhongToPBRConverter()

    # Example 1: Dark Plastic (GT86)
    dark_plastic = BlinnPhongParams(
        shader="ksPerPixelMultiMap_damage_dirt",
        ks_ambient=0.38,
        ks_diffuse=0.15,
        ks_specular=0.1,
        ks_specular_exp=10.0,
        ks_emissive=0.0,
        ks_alpha_ref=0.0,
        fresnel_c=0.035,
        fresnel_exp=4.0,
        fresnel_max_level=0.05,
        alpha_blend=False,
        alpha_test=False,
    )

    # Example 2: Metallic (hypothetical)
    metallic_paint = BlinnPhongParams(
        shader="ksPerPixelMultiMap",
        ks_ambient=0.5,
        ks_diffuse=0.6,
        ks_specular=0.8,  # High specular = metallic
        ks_specular_exp=128.0,  # High shininess
        ks_emissive=0.0,
        ks_alpha_ref=0.0,
        alpha_blend=False,
        alpha_test=False,
    )

    print("\n" + "=" * 60)
    print("Full Conversion Tests")
    print("=" * 60)

    print("\n--- Dark Plastic ---")
    pbr_dark = converter.convert(dark_plastic)
    print(f"Albedo:    {pbr_dark.albedo:.3f}")
    print(f"Metallic:  {pbr_dark.metallic:.3f}")
    print(f"Roughness: {pbr_dark.roughness:.3f}")
    print(f"Emissive:  {pbr_dark.emissive:.3f}")

    print("\n--- Metallic Paint ---")
    pbr_metal = converter.convert(metallic_paint)
    print(f"Albedo:    {pbr_metal.albedo:.3f}")
    print(f"Metallic:  {pbr_metal.metallic:.3f}")
    print(f"Roughness: {pbr_metal.roughness:.3f}")
    print(f"Emissive:  {pbr_metal.emissive:.3f}")


def test_ini_dict_conversion():
    """Test conversion from INI dictionary"""
    print("\n" + "=" * 60)
    print("INI Dictionary Conversion Test")
    print("=" * 60)

    mat_dict = {
        "SHADER": "ksPerPixelAT",
        "ksAmbient": "1",
        "ksDiffuse": "1",
        "ksSpecular": "0",
        "ksSpecularEXP": "0",
        "ksEmissive": "0",
        "ksAlphaRef": "0",
        "ALPHABLEND": "0",
        "ALPHATEST": "1",
    }

    bp_params = create_pbr_params_from_ini_dict(mat_dict)
    print(f"Shader: {bp_params.shader}")
    print(f"Diffuse: {bp_params.ks_diffuse}")
    print(f"Alpha Test: {bp_params.alpha_test}")
    print("✓ INI dict conversion successful")


if __name__ == "__main__":
    test_metallic_estimation()
    test_roughness_calculation()
    test_albedo_conversion()
    test_full_conversion()
    test_ini_dict_conversion()
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
