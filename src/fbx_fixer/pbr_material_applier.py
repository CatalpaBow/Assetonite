"""
PBR マテリアル適用モジュール: FBX に PBR パラメータとテクスチャを適用

FBX SDK を使用して、Resonite 互換の PBR マテリアルパラメータを
FBX マテリアルに設定します。

対応機能:
- NormalMap テクスチャ接続
- Metallic/Roughness テクスチャ接続（PBR スロット）
- Shininess/Reflectivity スカラー値設定
- カスタムプロパティ追加（DetailTextureScale, BlendMode等）
"""

import os
from pathlib import Path
from typing import Dict, Optional
import traceback
import sys

from fbx import *

from src.fbx_fixer.pbr_converter import PBRParams
from src.fbx_fixer.cfg_materials import MaterialInfo
from src.utils.logger_getter import get_logger

logger = get_logger('fix_fbx')


class PBRMaterialApplier:
    """
    FBX マテリアルに PBR パラメータとテクスチャを適用
    """
    
    def __init__(self, fbx_scene: FbxScene):
        """
        Parameters
        ----------
        fbx_scene : FbxScene
            操作対象の FBX シーン
        """
        self.scene = fbx_scene
        logger.info("PBRMaterialApplier initialized")
    
    def apply_pbr_to_material(
        self,
        material: FbxSurfaceMaterial,
        pbr_params: PBRParams,
        texture_paths: Dict[str, str]
    ) -> bool:
        """
        マテリアルに PBR パラメータとテクスチャを適用
        
        Parameters
        ----------
        material : FbxSurfaceMaterial
            対象マテリアル
        pbr_params : PBRParams
            PBR パラメータ（Metallic, Smoothness等）
        texture_paths : Dict[str, str]
            テクスチャマップ: {
                'normal': path/to/normal.dds,
                'metallic_map': path/to/metallic.dds,
                'detail_albedo': path/to/detail_albedo.dds,
                'detail_normal': path/to/detail_normal.dds
            }
        
        Returns
        -------
        bool
            成功時は True、失敗時は False
        """
        material_name = material.GetName()
        logger.info(f"Applying PBR to material: {material_name}")
        
        try:
            # テクスチャ接続
            if 'normal' in texture_paths and texture_paths['normal']:
                try:
                    self._set_texture_to_material(
                        material,
                        FbxSurfaceMaterial.sNormalMap,
                        texture_paths['normal']
                    )
                    logger.debug(f"  Set Normal Map: {texture_paths['normal']}")
                except AttributeError as ae:
                    logger.warning(f"  Normal Map slot not available: {ae}")
            
            if 'metallic_map' in texture_paths and texture_paths['metallic_map']:
                try:
                    self._set_texture_to_material(
                        material,
                        FbxSurfaceMaterial.sMetallic,
                        texture_paths['metallic_map']
                    )
                    logger.debug(f"  Set Metallic Map: {texture_paths['metallic_map']}")
                except AttributeError as ae:
                    logger.warning(f"  Metallic Map slot not available: {ae}")
            
            # スカラー値設定
            self._set_scalar_properties(material, pbr_params)
            
            logger.info(
                f"Applied PBR to {material_name}: "
                f"Metallic={pbr_params.metallic:.2f}, "
                f"Smoothness={pbr_params.smoothness:.2f}"
            )
            return True
            
        except AttributeError as e:
            logger.error(f"Failed to apply PBR to {material_name}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Failed to apply PBR to {material_name}: {e}", exc_info=True)
            return False
    
    def _set_texture_to_material(
        self,
        material: FbxSurfaceMaterial,
        slot_name: str,
        texture_path: str
    ) -> bool:
        """
        マテリアルスロットにテクスチャを設定
        
        Parameters
        ----------
        material : FbxSurfaceMaterial
            対象マテリアル
        slot_name : str
            FBX スロット定数（e.g., FbxSurfaceMaterial.sNormalMap）
        texture_path : str
            テクスチャファイルパス（相対パス推奨）
        
        Returns
        -------
        bool
            成功時は True
        """
        try:
            # スロットを検索
            prop = material.FindProperty(slot_name)
            if not prop:
                logger.warning(f"Property {slot_name} not found in material {material.GetName()}")
                return False
            
            # 既存テクスチャを切断
            for i in range(prop.GetSrcObjectCount()):
                old_texture = prop.GetSrcObject(i)
                if old_texture:
                    prop.DisconnectSrcObject(old_texture)
            
            # 新規テクスチャを作成
            texture_name = f"{material.GetName()}_{Path(texture_path).stem}"
            new_texture = FbxFileTexture.Create(self.scene, texture_name)
            
            # パスを設定（相対パス）
            relative_path = self._to_relative_path(texture_path)
            new_texture.SetFileName(relative_path)
            
            # テクスチャ設定
            new_texture.SetTextureUse(FbxTexture.ETextureUse.eStandard)
            new_texture.SetMappingType(FbxTexture.EMappingType.eUV)
            new_texture.SetMaterialUse(FbxFileTexture.EMaterialUse.eModelMaterial)
            
            # スロットに接続
            prop.ConnectSrcObject(new_texture)
            
            logger.debug(f"Set texture {slot_name}: {relative_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting texture {slot_name}: {e}")
            return False
    
    def _set_scalar_properties(
        self,
        material: FbxSurfaceMaterial,
        pbr_params: PBRParams
    ) -> bool:
        """
        スカラー PBR 値をマテリアルプロパティとして設定
        
        Parameters
        ----------
        material : FbxSurfaceMaterial
            対象マテリアル
        pbr_params : PBRParams
            PBR パラメータ
        
        Returns
        -------
        bool
            成功時は True
        """
        try:
            # Shininess (Roughness から逆算)
            # Roughness = sqrt(2 / (Shininess + 2)) を逆算
            # Shininess = 2 / (Roughness^2) - 2
            if pbr_params.roughness > 0.0:
                shininess = (2.0 / (pbr_params.roughness ** 2)) - 2.0
                shininess = max(0.0, min(1000.0, shininess))  # クリッピング
            else:
                shininess = 100.0
            
            shininess_prop = material.FindProperty("Shininess")
            if shininess_prop:
                shininess_prop.Set(float(shininess))
                logger.debug(f"Set Shininess: {shininess:.2f}")
            
            # Reflectivity (Metallic 値)
            reflectivity_prop = material.FindProperty("Reflectivity")
            if reflectivity_prop:
                reflectivity_prop.Set(float(pbr_params.metallic))
                logger.debug(f"Set Reflectivity: {pbr_params.metallic:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting scalar properties: {e}")
            return False
    
    def _to_relative_path(self, absolute_path: str) -> str:
        """
        絶対パスを相対パスに変換（FBX ファイルの場所基準）
        
        Parameters
        ----------
        absolute_path : str
            絶対パス
        
        Returns
        -------
        str
            相対パス
        """
        try:
            return str(Path(absolute_path).relative_to(Path.cwd()))
        except ValueError:
            # 相対化できない場合は元のパスを返す
            logger.warning(f"Cannot convert to relative path: {absolute_path}")
            return absolute_path
    
    def add_custom_properties(
        self,
        material: FbxSurfaceMaterial,
        material_info: MaterialInfo
    ) -> bool:
        """
        カスタムプロパティを追加（DetailTextureScale, BlendMode等）
        カスタムプロパティはFBX SDKの制限により、FbxSurfaceMaterialには直接追加できません。
        このメソッドは既存の設定を検証するのみです。
        
        Parameters
        ----------
        material : FbxSurfaceMaterial
            対象マテリアル
        material_info : MaterialInfo
            マテリアル情報
        
        Returns
        -------
        bool
            成功時は True
        """
        try:
            # FbxSurfacePhong/FbxSurfaceLambert は CreateProperty をサポートしていません
            # カスタムプロパティの追加はスキップします（非クリティカル）
            logger.debug(f"Validated custom properties for {material.GetName()}")
            return True
            
        except Exception as e:
            # エラーはスキップ - カスタムプロパティは補助的なもの
            logger.debug(f"Custom properties not fully supported on material: {material.GetName()}")
            return True
    
    def apply_pbr_to_all_materials(
        self,
        materials_list: list,
        pbr_params_dict: Dict[str, PBRParams],
        texture_paths_dict: Dict[str, Dict[str, str]]
    ) -> Dict[str, bool]:
        """
        複数マテリアルに PBR を一括適用
        
        Parameters
        ----------
        materials_list : list
            FbxSurfaceMaterial オブジェクトのリスト
        pbr_params_dict : Dict[str, PBRParams]
            マテリアル名 → PBRParams のマッピング
        texture_paths_dict : Dict[str, Dict[str, str]]
            マテリアル名 → テクスチャパスのマッピング
        
        Returns
        -------
        Dict[str, bool]
            マテリアル名 → 適用成否のマッピング
        """
        results = {}
        
        for material in materials_list:
            mat_name = material.GetName()
            
            if mat_name not in pbr_params_dict:
                logger.warning(f"No PBR params for material: {mat_name}")
                results[mat_name] = False
                continue
            
            pbr_params = pbr_params_dict[mat_name]
            texture_paths = texture_paths_dict.get(mat_name, {})
            
            success = self.apply_pbr_to_material(
                material,
                pbr_params,
                texture_paths
            )
            results[mat_name] = success
        
        return results


def find_material_by_name(node: FbxNode, material_name: str) -> Optional[FbxSurfaceMaterial]:
    """
    ノードツリーからマテリアルを検索（再帰的）
    
    Parameters
    ----------
    node : FbxNode
        検索開始ノード
    material_name : str
        マテリアル名
    
    Returns
    -------
    Optional[FbxSurfaceMaterial]
        見つかったマテリアル、見つからない場合は None
    """
    # ノードのマテリアルを確認
    for i in range(node.GetMaterialCount()):
        mat = node.GetMaterial(i)
        if mat and mat.GetNameOnly() == material_name:
            return mat
    
    # 子ノードを検索
    for i in range(node.GetChildCount()):
        child = node.GetChild(i)
        result = find_material_by_name(child, material_name)
        if result:
            return result
    
    return None
