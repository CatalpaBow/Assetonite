"""
テクスチャ統合モジュール: AC (Blinn-Phong) テクスチャ → Resonite PBR テクスチャ変換

AC の scatter テクスチャセット (txDiffuse, txMaps, txNormal, txDetail) を
Resonite (Metallic-Roughness PBR) 最終フォーマットに変換します。

変換結果:
  - Albedo (BC7)
  - Normal (BC5)
  - DetailAlbedo (BC7)
  - DetailNormal (BC5)
  - MetallicMap (BC7): R=Metallic, G=AO, B=Unused, A=Smoothness
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

from src.fbx_fixer.dds_to_dds_converter import DDStoXFormatter
from src.fbx_fixer.texconv_wrapper import TexConvWrapper
from src.fbx_fixer.pbr_converter import PBRParams
from src.fbx_fixer.cfg_materials import MaterialInfo
from src.utils.logger_getter import get_logger

logger = get_logger('fix_fbx')


class TextureIntegrator:
    """
    AC テクスチャを Resonite PBR フォーマットに統合変換
    """
    
    def __init__(self, output_folder: Path):
        """
        Parameters
        ----------
        output_folder : Path
            変換済みテクスチャの出力先ディレクトリ
        """
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.dds_converter = DDStoXFormatter()
        logger.info(f"TextureIntegrator initialized: output={output_folder}")
    
    def convert_all_textures(
        self,
        material_info: MaterialInfo,
        pbr_params: PBRParams,
        material_name: str
    ) -> Dict[str, str]:
        """
        マテリアルの全テクスチャを Resonite フォーマットに変換
        
        Parameters
        ----------
        material_info : MaterialInfo
            AC マテリアル情報（テクスチャパス含む）
        pbr_params : PBRParams
            PBR パラメータ（Metallic, Roughness, Smoothness）
        material_name : str
            マテリアル名（出力ファイル命名用）
        
        Returns
        -------
        Dict[str, str]
            {texture_type: output_path}
            例: {
                'albedo': 'output/material_albedo.dds',
                'normal': 'output/material_normal.dds',
                'metallic_map': 'output/material_metallic.dds',
                'detail_albedo': 'output/material_detail_albedo.dds',
                'detail_normal': 'output/material_detail_normal.dds'
            }
        """
        logger.info(f"Converting textures for material: {material_name}")
        
        output_textures = {}
        
        # txDiffuse → Albedo (BC7)
        if 'txDiffuse' in material_info.textures:
            albedo_path = self.convert_diffuse_to_albedo(
                material_info.textures['txDiffuse'].texture_path,
                material_name
            )
            if albedo_path:
                output_textures['albedo'] = albedo_path
                logger.debug(f"  Albedo: {albedo_path}")
        
        # txNormal → Normal (BC5)
        if 'txNormal' in material_info.textures:
            normal_path = self.convert_normal_to_normal_map(
                material_info.textures['txNormal'].texture_path,
                material_name
            )
            if normal_path:
                output_textures['normal'] = normal_path
                logger.debug(f"  Normal: {normal_path}")
        
        # txMaps → MetallicMap (BC7)
        # AC では txMaps が R=Specular, G=Sharpness, B=AO
        if 'txMaps' in material_info.textures:
            metallic_map_path = self.convert_txmaps_to_metallic_map(
                material_info.textures['txMaps'].texture_path,
                pbr_params,
                material_name
            )
            if metallic_map_path:
                output_textures['metallic_map'] = metallic_map_path
                logger.debug(f"  MetallicMap: {metallic_map_path}")
        
        # txDetail → DetailAlbedo (BC7)
        if 'txDetail' in material_info.textures:
            detail_albedo_path = self.convert_detail_to_detail_albedo(
                material_info.textures['txDetail'].texture_path,
                material_name
            )
            if detail_albedo_path:
                output_textures['detail_albedo'] = detail_albedo_path
                logger.debug(f"  DetailAlbedo: {detail_albedo_path}")
        
        # txDetailNM / txNormalDetail → DetailNormal (BC5)
        detail_normal_key = next(
            (k for k in material_info.textures.keys() if 'detail' in k.lower() and 'nm' in k.lower() or 'normal' in k.lower()),
            None
        )
        if detail_normal_key:
            detail_normal_path = self.convert_detail_normal_map(
                material_info.textures[detail_normal_key].texture_path,
                material_name
            )
            if detail_normal_path:
                output_textures['detail_normal'] = detail_normal_path
                logger.debug(f"  DetailNormal: {detail_normal_path}")
        
        logger.info(f"Completed texture conversion for {material_name}: {len(output_textures)} textures")
        return output_textures
    
    def convert_diffuse_to_albedo(self, diffuse_path: str, material_name: str) -> Optional[str]:
        """
        txDiffuse → Albedo (BC7)
        
        Parameters
        ----------
        diffuse_path : str
            AC txDiffuse DDS ファイルパス
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            出力 Albedo ファイルパス、失敗時は None
        """
        if not Path(diffuse_path).exists():
            logger.warning(f"Diffuse texture not found: {diffuse_path}")
            return None
        
        output_path = self.output_folder / f"{material_name}_albedo.dds"
        
        try:
            # BC7_UNORM_SRGB フォーマットに変換（カラーテクスチャ用 sRGB）
            self.dds_converter.convert(
                diffuse_path,
                str(output_path),
                format="BC7_UNORM_SRGB"
            )
            logger.debug(f"Converted Diffuse → Albedo: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to convert diffuse: {e}")
            return None
    
    def convert_normal_to_normal_map(self, normal_path: str, material_name: str) -> Optional[str]:
        """
        txNormal → Normal (BC5)
        
        Parameters
        ----------
        normal_path : str
            AC txNormal DDS ファイルパス
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            出力 Normal ファイルパス、失敗時は None
        """
        if not Path(normal_path).exists():
            logger.warning(f"Normal texture not found: {normal_path}")
            return None
        
        output_path = self.output_folder / f"{material_name}_normal.dds"
        
        try:
            # BC5_UNORM フォーマットに変換（RG チャネル保持、リニア）
            self.dds_converter.convert(
                normal_path,
                str(output_path),
                format="BC5_UNORM"
            )
            logger.debug(f"Converted Normal → Normal: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to convert normal: {e}")
            return None
    
    def convert_txmaps_to_metallic_map(
        self,
        txmaps_path: str,
        pbr_params: PBRParams,
        material_name: str
    ) -> Optional[str]:
        """
        txMaps (R8G8_UNORM) → MetallicMap (BC7, RGBA)
        
        ⚠️ 重要: ezTexConv は R8G8_UNORM 形式をサポートしません。
        事前に texConv (Microsoft) で RGB 形式に変換してから処理します。
        
        AC の txMaps は以下のレイアウト:
          R: Specular Brightness (0-255)
          G: Metallic or Sharpness (0-255)
          B: AO / Reflection (0-255)
          A: (未使用 or Alpha)
        
        変換結果 MetallicMap (BC7):
          R: Metallic (推定値, pbr_params.metallic を 0-255 に正規化)
          G: AO (txMaps.B をそのまま使用)
          B: 0 (unused)
          A: Smoothness (計算値, 0-255)
        
        Parameters
        ----------
        txmaps_path : str
            AC txMaps DDS ファイルパス (R8G8_UNORM or R8G8B8A8)
        pbr_params : PBRParams
            PBR パラメータ (metallic, smoothness 含む)
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            出力 MetallicMap ファイルパス、失敗時は None
        """
        if not Path(txmaps_path).exists():
            logger.warning(f"txMaps texture not found: {txmaps_path}")
            return None
        
        output_path = self.output_folder / f"{material_name}_metallic.dds"
        
        try:
            # ステップ 1: R8G8_UNORM フォーマット検出
            # texConv (Microsoft) で RGB 形式に事前変換（ezTexConv 対応）
            txmaps_input = self._ensure_rgb_format(txmaps_path, material_name)
            if not txmaps_input:
                logger.error(f"Failed to convert txMaps to RGB format: {txmaps_path}")
                return None
            
            # ステップ 2: ezTexConv でチャネルマッピング＋BC7 変換
            wrapper = TexConvWrapper(texconv_path=r'.tools\ezTexConv.exe')
            
            # 入力: RGB 形式に変換済み txMaps
            wrapper.add_input(0, txmaps_input)
            
            # チャネルマッピング
            # R: Metallic (pbr_params.metallic を 0-255 に正規化)
            wrapper.set_channel_map('r', 'white' if pbr_params.metallic > 0.5 else 'black')
            # 簡易実装: Metallic が高い場合は白、低い場合は黒
            # TODO: より正確には pbr_params.metallic を DDS に埋め込む
            
            # G: AO (txMaps.B) txMapsにおいて一般的にRかBにAOが使用されるので割り当て
            wrapper.set_channel_map('g', 'in0.b')
            
            # B: unused
            wrapper.set_channel_map('b', 'black')
            
            # A: Smoothness (pbr_params.smoothness を 0-255 に正規化)
            # TODO: smoothness 値を DDS に埋め込む
            wrapper.set_channel_map('a', 'white' if pbr_params.smoothness > 0.5 else 'black')
            
            # フォーマット: BC7_UNORM (リニア、グレースケール/MetallicMap用)
            wrapper.set_option('-f', 'BC7_UNORM')
            wrapper.set_output(str(output_path))
            
            # 実行
            wrapper.run()
            
            logger.debug(f"Converted txMaps → MetallicMap: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to convert txMaps: {e}")
            return None
    
    def _ensure_rgb_format(self, dds_path: str, material_name: str) -> Optional[str]:
        """
        DDS が R8G8_UNORM / R8_UNORM の場合、RGB 形式に変換
        
        ⚠️ ezTexConv は RGB ベースの形式のみサポート。
        texConv (Microsoft) を使用して事前変換が必要。
        
        Parameters
        ----------
        dds_path : str
            DDS ファイルパス
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            RGB 形式の DDS パス、変換不要な場合は元のパス
        """
        from dds_formater import is_r8g8
        
        path = Path(dds_path)
        
        # フォーマット判定
        if not is_r8g8(path):
            # RGB 形式既に対応している、そのまま返す
            logger.debug(f"txMaps is already RGB format: {dds_path}")
            return dds_path
        
        # R8G8_UNORM の場合、texConv (Microsoft) で RGB に変換
        logger.info(f"Converting R8G8_UNORM to RGB for {material_name}...")
        
        try:
            rgb_output_path = self.output_folder / f"{material_name}_txmaps_rgb.dds"
            
            # texConv (Microsoft) を使用して R8G8B8A8_UNORM に変換
            self.dds_converter.convert(
                str(dds_path),
                str(rgb_output_path),
                format="R8G8B8A8_UNORM"
            )
            
            logger.debug(f"Converted R8G8_UNORM to RGB: {rgb_output_path}")
            return str(rgb_output_path)
            
        except Exception as e:
            logger.error(f"Failed to convert R8G8_UNORM to RGB: {e}")
            return None
    
    def convert_detail_to_detail_albedo(self, detail_path: str, material_name: str) -> Optional[str]:
        """
        txDetail → DetailAlbedo (BC7)
        
        Parameters
        ----------
        detail_path : str
            AC txDetail DDS ファイルパス
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            出力 DetailAlbedo ファイルパス、失敗時は None
        """
        if not Path(detail_path).exists():
            logger.warning(f"Detail texture not found: {detail_path}")
            return None
        
        output_path = self.output_folder / f"{material_name}_detail_albedo.dds"
        
        try:
            # BC7_UNORM_SRGB フォーマットに変換（カラーテクスチャ用）
            self.dds_converter.convert(
                detail_path,
                str(output_path),
                format="BC7_UNORM_SRGB"
            )
            logger.debug(f"Converted Detail → DetailAlbedo: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to convert detail: {e}")
            return None
    
    def convert_detail_normal_map(self, detail_normal_path: str, material_name: str) -> Optional[str]:
        """
        txDetailNM / txNormalDetail → DetailNormal (BC5)
        
        Parameters
        ----------
        detail_normal_path : str
            AC txDetailNM DDS ファイルパス
        material_name : str
            マテリアル名
        
        Returns
        -------
        Optional[str]
            出力 DetailNormal ファイルパス、失敗時は None
        """
        if not Path(detail_normal_path).exists():
            logger.warning(f"Detail normal texture not found: {detail_normal_path}")
            return None
        
        output_path = self.output_folder / f"{material_name}_detail_normal.dds"
        
        try:
            # BC5_UNORM フォーマットに変換（RG チャネル、リニア）
            self.dds_converter.convert(
                detail_normal_path,
                str(output_path),
                format="BC5_UNORM"
            )
            logger.debug(f"Converted DetailNM → DetailNormal: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to convert detail normal: {e}")
            return None
    
    def _normalize_metallic_to_255(self, metallic: float) -> int:
        """Metallic (0-1) を DDS グレースケール (0-255) に正規化"""
        return max(0, min(255, int(metallic * 255)))
    
    def _normalize_smoothness_to_255(self, smoothness: float) -> int:
        """Smoothness (0-1) を DDS グレースケール (0-255) に正規化"""
        return max(0, min(255, int(smoothness * 255)))
    
    def _to_relative_path(self, absolute_path: str) -> str:
        """
        絶対パスを相対パスに変換（現在の作業ディレクトリ基準）
        
        Parameters
        ----------
        absolute_path : str
            絶対パス
        
        Returns
        -------
        str
            相対パス、変換不可の場合は元のパス
        """
        try:
            return str(Path(absolute_path).relative_to(Path.cwd()))
        except ValueError:
            # 相対化できない場合は元のパスを返す（異なるドライブなど）
            logger.warning(f"Cannot convert to relative path: {absolute_path}")
            return absolute_path
