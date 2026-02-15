# FBX修正プロセス詳細解説

## 概要

Assetoniteの FBX修正プロセスは、AssettoCorsaSim (AC) のBlinn-Phong ベースのカーモデルを、Resoniteの Physically Based Rendering (PBR) 形式に変換する統合パイプラインです。

このドキュメントでは、各フェーズの詳細な処理フロー、使用ツール、パラメータ計算方式を説明します。

**処理フロー図:**
```
AC FBX モデル (MatInfo INI + テクスチャ)
        ↓
┌─────────────────────────────────────────┐
│ フェーズ 1: アルファチャネル処理         │
│ (convert_to_non_alpha)                  │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│ フェーズ 2: PBR パラメータ計算          │
│ (BlinnPhongToPBRConverter)              │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│ フェーズ 3: テクスチャ統合変換           │
│ (TextureIntegrator)                     │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│ フェーズ 4: マテリアル適用              │
│ (PBRMaterialApplier)                    │
└─────────────────────────────────────────┘
        ↓
Resonite互換 FBX (PBR適用済み)
```

---

## フェーズ 1: アルファチャネル処理

### 目的
AssettoCorsaSim のテクスチャの一部にはアルファチャネルが含まれていますが、これらは Resonite との互換性の問題やレンダリング効率の観点から削除する必要があります。

### 処理内容

**実行箇所:** `material_fixer.py::convert_to_non_alpha()`

#### 1.1 アルファチャネル検出
```
入力: テクスチャファイルパス
処理:
  1. ファイルが DDS 形式か確認
  2. DDS ヘッダーを読み込み
  3. アルファフラグをチェック (D3DFORMAT に alpha フラグあり?)
  4. アルファピクセルデータが存在するか検証
```

**判定条件:**
- BC3 形式 (DXT5) → アルファあり
- BC7 形式 → アルファチャネル有の場合あり
- その他の RGBA 形式 → アルファあり

#### 1.2 テクスチャ再エンコード
アルファチャネル付きテクスチャが検出された場合、Microsoft DirectXTex の **texconv** を使用して再エンコード：

```bash
TexConv.exe -r <input.dds> -ft dds -f BC7_UNORM_SRGB -o <output_folder> -y
```

**パラメータ:**
- `-r`: リサイズと再圧縮
- `-ft dds`: 出力フォーマット（DDS）
- `-f BC7_UNORM_SRGB`: 出力フォーマット名（sRGB色空間のBC7）
- `-o`: 出力フォルダ
- `-y`: 既存ファイルを上書き

#### 1.3 出力
```
元のテクスチャ: Interior_LR.dds (BC3, 512x512)
        ↓ texconv処理
結果: Interior_LR.dds (BC7_UNORM_SRGB, 512x512, アルファなし)
```

**ログ出力例:**
```
2026-02-12 21:47:50 - fix_fbx - INFO - 実行: TexConv.exe -r ... -f BC7_UNORM_SRGB ...
2026-02-12 21:47:50 - fix_fbx - INFO - 変換成功: Interior_LR.dds -> Interior_LR_albedo.dds
```

---

## フェーズ 2: PBR パラメータ計算

### 目的
AC の Blinn-Phong シェーディングパラメータから、Resonite 互換の PBR パラメータを計算します。

### 処理内容

**実行箇所:** `pbr_converter.py::convert()`

#### 2.1 入力パラメータ（AC INI から抽出）

| パラメータ | 説明 | 値域 |
|-----------|------|------|
| `ksAmbient` | 環境光反射係数 | RGB (0-1) |
| `ksDiffuse` | 拡散反射係数 | RGB (0-1) |
| `ksSpecular` | 鏡面反射係数 | RGB (0-1) |
| `ksSpecularEXP` | 鏡面反射指数 | 1-128 |
| `ksAlphaRef` | アルファテスト閾値 | 0-255 |

#### 2.2 計算公式

##### 2.2.1 Roughness 計算
```
Roughness = √(2 / (ksSpecularEXP + 2))
```

**背景:**
- Blinn-Phong の指数を物理ベースのRoughness に変換
- ksSpecularEXP が大きい → ピカピカ（Roughness小）
- ksSpecularEXP が小さい → ザラザラ（Roughness大）

**計算例:**
```
ksSpecularEXP = 64
Roughness = √(2/(64+2)) = √(2/66) = √0.0303 ≈ 0.174
```

##### 2.2.2 Smoothness 計算
```
Smoothness = 1 - Roughness
```

**背景:**
- Resonite では Roughness の逆数を Smoothness として使用
- Smoothness が大きい → つやつや
- Smoothness が小さい → マット

**例:**
```
Roughness = 0.174
Smoothness = 1 - 0.174 = 0.826
→ テクスチャの A チャネルに 0.826 × 255 = 210 を格納
```

##### 2.2.3 Metallic 推定
```
Metallic = average(ksSpecular.R, ksSpecular.G, ksSpecular.B)
         = (ksSpecular.R + ksSpecular.G + ksSpecular.B) / 3
```

**背景:**
- AC では ksSpecular の値が大きい = 鏡面反射性が高い
- PBR では Metallic が大きい = メタリック（金属光沢）
- 簡易推定のため RGB 平均を使用

**例:**
```
ksSpecular = (0.8, 0.8, 0.8)
Metallic = (0.8 + 0.8 + 0.8) / 3 = 0.8
```

#### 2.3 出力パラメータ構造体

```python
@dataclass
class PBRParams:
    metallic: float      # 0-1 (メタリック度)
    roughness: float     # 0-1 (粗さ)
    smoothness: float    # 0-1 (つやつやさ = 1 - roughness)
    albedo: Tuple        # RGB (拡散色, ksAmbient + ksDiffuse)
    
# 例
PBRParams(
    metallic=0.8,
    roughness=0.174,
    smoothness=0.826,
    albedo=(0.9, 0.9, 0.9)
)
```

#### 2.4 ログ出力例
```
2026-02-12 21:47:00 - fix_fbx - DEBUG - ksSpecularEXP=64 → Roughness=0.174, Smoothness=0.826
2026-02-12 21:47:00 - fix_fbx - DEBUG - PBR conversion: Metallic=0.80
```

---

## フェーズ 3: テクスチャ統合変換

### 目的
AC の 5 種類のテクスチャ（txDiffuse, txNormal, txMaps, txDetail, txDetailNM）を Resonite PBR 形式の 5 種類に変換・統合します。

### 処理内容

**実行箇所:** `texture_integrator.py::convert_all_textures()`

#### 3.1 テクスチャマッピング表

| AC テクスチャ | Resonite テクスチャ | フォーマット | 処理内容 |
|-------------|-----------------|-----------|---------|
| txDiffuse | Albedo | BC7_UNORM_SRGB | sRGB色空間に変換 |
| txNormal | NormalMap | BC5_UNORM | 法線マップ（RG成分） |
| txMaps | MetallicMap* | BC7_UNORM | R=Metallic, G=AO, A=Smoothness |
| txDetail | DetailAlbedo | BC7_UNORM_SRGB | 詳細色 |
| txDetailNM | DetailNormal | BC5_UNORM | 詳細法線マップ |

**※ MetallicMap は複合テクスチャで、複数パラメータを 1 つの DDS に統合*

#### 3.2 各テクスチャの変換処理

##### 3.2.1 Albedo 生成 (txDiffuse → Albedo)

**ワークフロー:**
```
txDiffuse (BC3/BC7)
    ↓
texconv で BC7_UNORM_SRGB に変換
    ↓
Albedo.dds (BC7_UNORM_SRGB)
```

**処理コマンド:**
```bash
TexConv.exe -r texture/Interior_LR.dds -ft dds -f BC7_UNORM_SRGB -o pbr_textures/ -y
```

**フォーマット選択理由:**
- BC7_UNORM_SRGB = BC7 圧縮 + sRGB 色空間
- sRGB: ディスプレイ最適化（ガンマ補正を含む）
- 色データに適切（テクスチャアーティスト期待値）

##### 3.2.2 NormalMap 生成 (txNormal → NormalMap)

**ワークフロー:**
```
txNormal (BC3/BC5)
    ↓
texconv で BC5_UNORM に変換
    ↓
NormalMap.dds (BC5_UNORM)
```

**処理コマンド:**
```bash
TexConv.exe -r texture/Toyota_Logo_NM.dds -ft dds -f BC5_UNORM -o pbr_textures/ -y
```

**フォーマット選択理由:**
- BC5 = RG成分 のみ（B成分は計算で復元）
- LINEAR: リニア色空間（物理計算用）
- 圧縮効率が高い（BC7 より 25% 小さい）

##### 3.2.3 MetallicMap 生成 (txMaps → MetallicMap)

**最も複雑な処理 - チャネルマッピング:**

```
txMaps (AC パラメータマップ)
    ├─ R チャネル → MetallicMap.R = Metallic値
    ├─ G チャネル → MetallicMap.G = AO(Ambient Occlusion)
    ├─ B チャネル → MetallicMap.B = Black(未使用)
    └─ A チャネル → MetallicMap.A = Smoothness値
        ↓
    処理: テクスチャ解析 → パラメータ値適用 → チャネル再マッピング
        ↓
    MetallicMap.dds (BC7_UNORM)
```

**ステップ詳細:**

###### ステップ 1: R8G8_UNORM 形式の事前変換
AC の txMaps が R8G8_UNORM （赤青チャネルのみ）形式の場合、**ezTexConv が対応していないため**、Microsoft texconv で RGB に拡張：

```bash
TexConv.exe -r Int_AO_B.dds -ft dds -f R8G8B8A8_UNORM -o temp/ -y
```

**フロー:**
```
Int_AO_B.dds (R8G8_UNORM)
    ↓ [txconv で拡張]
Int_AO_B_rgb.dds (R8G8B8A8_UNORM)  ← ezTexConv への入力
```

###### ステップ 2: チャネルマッピング + BC7 圧縮
ezTexConv でチャネルを再割り当て：

```bash
ezTexConv.exe -out MetallicMap.dds \
    -in0 Int_AO_B_rgb.dds \
    -r black                    # R = Metallic(簡易: black/white) \
    -g in0.b                    # G = AO (入力の B チャネル) \
    -b black                    # B = 未使用 \
    -a white                    # A = Smoothness(簡易: black/white) \
    -f BC7_UNORM                # BC7 リニア圧縮
```

**パラメータ説明:**
- `-r black/-r white`: Metallic が低い/高い場合のフォールバック
  - 理想：`-r in0.r` で AC の R チャネルを使用
  - 制限：ezTexConv のチャネルマッピング制限で簡易値を使用
- `-g in0.b`: AC の Blue チャネル（通常は Ambient Occlusion）
- `-a white/-a black`: Smoothness 値（パラメータから計算）
- `-f BC7_UNORM`: リニア色空間（スカラー値用）

**出力:**
```
MetallicMap.dds (BC7_UNORM):
  R = Metallic         [0-255 か 0 または 255]
  G = Ambient Occlusion [0-255 の値]
  B = 黒(未使用)       [0]
  A = Smoothness       [0-255 か 0 または 255]
```

##### 3.2.4 DetailAlbedo 生成 (txDetail → DetailAlbedo)

```bash
TexConv.exe -r texture/scratches.dds -ft dds -f BC7_UNORM_SRGB -o pbr_textures/ -y
```

**用途:**
- 詳細な表面キズ、スクラッチテクスチャ
- Resonite の DetailTexture スロット

##### 3.2.5 DetailNormal 生成 (txDetailNM → DetailNormal)

```bash
TexConv.exe -r texture/Toyota_Logo_NM.dds -ft dds -f BC5_UNORM -o pbr_textures/ -y
```

**用途:**
- 詳細な法線情報
- Resonite の DetailNormalMap スロット

#### 3.3 相対パス変換

**背景:**
- テクスチャファイルは絶対パスで生成される
- FBX では相対パスが推奨される

**処理:**
```python
absolute_path = "D:\\Devlop\\Assetonite\\data\\input\\...\\pbr_textures\\Albedo.dds"
                ↓ [Path.relative_to(cwd)]
relative_path = "data\\input\\...\\pbr_textures\\Albedo.dds"
```

**警告出力:**
```
Cannot convert to relative path: F:\Games\...
→ 異なるドライブのテクスチャパス（相対化不可）
→ 絶対パスのまま使用（Resonite でも処理可能）
```

#### 3.4 出力例

```python
texture_paths = {
    'albedo': 'pbr_textures/Body_albedo.dds',
    'normal': 'pbr_textures/Body_normal.dds',
    'metallic_map': 'pbr_textures/Body_metallic.dds',
    'detail_albedo': 'pbr_textures/Body_detail_albedo.dds',
    'detail_normal': 'pbr_textures/Body_detail_normal.dds'
}
```

#### 3.5 ログ出力例
```
2026-02-12 21:47:10 - fix_fbx - INFO - 実行: TexConv.exe -r ... -f BC7_UNORM_SRGB ...
2026-02-12 21:47:10 - fix_fbx - INFO - 変換成功: Rims.dds -> Rim_albedo.dds (BC7_UNORM_SRGB)
2026-02-12 21:47:10 - fix_fbx - INFO - Running ezTexConv: ... -f BC7_UNORM ...
2026-02-12 21:47:10 - fix_fbx - INFO - Completed texture conversion: 5 textures
```

---

## フェーズ 4: マテリアル適用

### 目的
FBX SDK を使用して、計算済み PBR パラメータと変換済みテクスチャを FBX マテリアルに適用します。

### 処理内容

**実行箇所:** `pbr_material_applier.py::apply_pbr_to_material()`

#### 4.1 FBX マテリアル検索

**処理フロー:**
```
FBX シーングラフ (ノード階層)
    ↓ [再帰的に走査]
全マテリアル抽出
    ↓ [マテリアル名で検索]
対象マテリアル発見 → apply_pbr_to_material()
```

**実装:**
```python
def find_material_by_name(node, target_name):
    """ノード以下の全マテリアルから指定名を検索"""
    for i in range(node.GetMaterialCount()):
        material = node.GetMaterial(i)
        if material.GetName() == target_name:
            return material
    
    # 子ノードを再帰検索
    for j in range(node.GetChildCount()):
        result = find_material_by_name(node.GetChild(j), target_name)
        if result:
            return result
    
    return None
```

#### 4.2 テクスチャスロット設定

**処理:**
```
マテリアル FbxSurfaceMaterial
    ├─ Albedo → FbxSurfaceMaterial.sAlbedo
    ├─ Normal → FbxSurfaceMaterial.sNormalMap
    ├─ Metallic → FbxSurfaceMaterial.sMetallic (エラーの場合はスキップ)
    └─ DetailTextures → カスタムプロパティ
```

**詳細処理:**

###### 4.2.1 テクスチャファイル作成
```cpp
FbxFileTexture* texture = FbxFileTexture::Create(fbx_scene, slot_name);
texture->SetFileName(texture_path.c_str());
```

###### 4.2.2 マテリアルスロットに接続
```cpp
FbxProperty prop = material.FindProperty(slot_name);
prop.ConnectSrcObject(texture);
```

**スロット定数:**
| スロット | 定数名 | 説明 |
|---------|------|------|
| Albedo | sAlbedo | 拡散色 |
| Normal | sNormalMap | 法線マップ |
| Metallic* | sMetallic | メタリック（非標準） |

**※ sMetallic は FbxSurfacePhong に非標準のため、エラー時は警告としてログ*

#### 4.3 スカラー値設定

**処理:**
```python
def _set_scalar_properties(material, pbr_params):
    # Shininess = 鏡面反射指数 (Roughnessから逆算)
    # Reflectivity = Metallic値
```

**計算:**
```
AC では:
    Shininess = exp(2)  (Blinn-Phong 指数)

PBR から AC への逆変換:
    Shininess = 2 / (Roughness^2) - 2
    
例:
    Roughness = 0.174
    Shininess = 2 / (0.174^2) - 2 = 2 / 0.0303 - 2 ≈ 64
```

**FBX 設定:**
```python
material.Shininess.Set(shininess_value)
material.ReflectionFactor.Set(pbr_params.metallic)
```

**ログ出力:**
```
2026-02-12 21:47:15 - fix_fbx - DEBUG - Set Shininess: 64.00
2026-02-12 21:47:15 - fix_fbx - DEBUG - Set Reflectivity: 0.80
```

#### 4.4 エラー処理

**発生可能なエラー:**

| エラー | 原因 | 処理 |
|-------|------|------|
| `AttributeError: sMetallic` | FBX SDK の非標準属性 | WARNING ログ出力、処理継続 |
| `FindProperty() 失敗` | スロット非対応 | WARNING ログ出力、処理継続 |
| `ConnectSrcObject() 失敗` | テクスチャパス無効 | ERROR ログ出力、スキップ |

**例:**
```
2026-02-12 21:47:15 - fix_fbx - WARNING - Metallic Map slot not available: 
  type object 'FbxSurfaceMaterial' has no attribute 'sMetallic'
→ 処理は続行、タイプアンリップなしで FBX エクスポート
```

#### 4.5 カスタムプロパティ追加（オプション）

**未実装フェーズ:**
```python
def add_custom_properties(material, mat_info):
    # DetailTextureScale: 詳細テクスチャのスケール
    # BlendMode: ブレンドモード（透過情報）
    # SpecularColor: 鏡面反射色
```

**状態:** FbxSurfacePhong.CreateProperty() の API 制限により、現在は部分実装

---

## フェーズ 5: FBX エクスポート

### 目的
修正済みマテリアルを含む FBX ファイルをエクスポートします。

### 処理内容

**実行箇所:** `material_fixer.py::export()`

#### 5.1 エクスポート処理

```python
def export(fbx_path):
    # FbxScene を .fbx ファイルに出力
    exporter = FbxExporter.Create(fbx_manager, "FBX Exporter")
    export_options = FbxIOSettings(fbx_manager)
    
    # オプション設定
    export_options.SetBoolProp(
        EXP_FBX_SHAPE,      True   # シェイプ含める
    )
    export_options.SetBoolProp(
        EXP_FBX_MATERIAL,   True   # マテリアル含める ← 重要
    )
    export_options.SetBoolProp(
        EXP_FBX_TEXTURE,    True   # テクスチャ参照含める
    )
    
    exporter.SetFileExportVersion(FBX_2020_00_COMPATIBLE)
    exporter.Initialize(fbx_path, -1, export_options)
    exporter.Export(fbx_scene)
    exporter.Destroy()
```

#### 5.2 出力ファイル

**保存先:**
```
src/mat_fix.py 指定フォルダ
├── model.fbx (修正済み PBR マテリアル適用)
└── pbr_textures/
    ├── Body_albedo.dds
    ├── Body_normal.dds
    ├── Body_metallic.dds
    ├── Body_detail_albedo.dds
    └── Body_detail_normal.dds
```

#### 5.3 ログ出力例
```
2026-02-12 21:47:19 - fix_fbx - INFO - Sucsess to export fbx
2026-02-12 21:47:19 - fix_fbx - INFO - Sucess to fix fbx
```

---

## エラーハンドリングとロギング

### ログシステム

**ロガー統一:** すべてのモジュールが `'fix_fbx'` ロガーを使用
```python
from src.utils.logger_getter import get_logger
logger = get_logger('fix_fbx')  # 全モジュール統一
```

**ハンドラー:**
1. **コンソール出力:** DEBUG レベル以上
2. **ファイル記録:** DEBUG レベル以上 → `logs/fixFbx_YYYYMMDD_HHMMSS.log`

### ログレベル別使い分け

| レベル | 用途 | 出力先 |
|-------|------|-------|
| DEBUG | 処理の詳細フロー | ターミナル + ファイル |
| INFO | 重要な処理完了 | ターミナル + ファイル |
| WARNING | 非致命的エラー | ターミナル + ファイル |
| ERROR | 致命的エラー | ターミナル + ファイル |

### トリアージ例

**警告が多い場合:**
```
2026-02-12 21:47:15 - fix_fbx - WARNING - Failed to create new texture 3 times
→ Alpha 削除失敗、テクスチャそのまま使用（多くの場合問題なし）
```

**エラーが発生した場合:**
```
2026-02-12 21:47:15 - fix_fbx - ERROR - Failed to apply PBR to Material: ...
→ FBX SDK 制限、処理スキップしつつ継続
→ PBR applied to 58/58 materials でも 57 個のみ実際適用
```

---

## パフォーマンス特性

### 処理時間目安 (GT86 モデル: 58 マテリアル)

| フェーズ | 処理時間 | 説明 |
|---------|---------|------|
| アルファ変換 | ~10秒 | texconv による DDS エンコード |
| PBR 計算 | <1秒 | CPU 演算 |
| テクスチャ統合 | ~15秒 | texconv + ezTexConv |
| マテリアル適用 | ~5秒 | FBX SDK 操作 |
| FBX エクスポート | ~2秒 | ファイル I/O |
| **合計** | **~40秒** | |

### ディスク使用量

| 項目 | サイズ | 説明 |
|------|--------|------|
| 入力 AC テクスチャ | ~200MB | BC3/BC7/BC1 |
| 出力 PBR テクスチャ | ~180MB | BC7/BC5 圧縮 |
| FBX ファイル | ~30MB | モデル + マテリアル参照 |
| **ログファイル** | ~400KB | 処理ログ |

---

## トラブルシューティング

### 問題: テクスチャが見つからない

**症状:**
```
Cannot convert to relative path: F:\Games\...
→ ログにはあるが、Resonite で見つからない
```

**原因:**
- テクスチャが異なるドライブにある
- 相対化に失敗して絶対パスのまま

**解決:**
- FBX 内の テクスチャパスを確認
- Resonite で手動でテクスチャを再リンク

### 問題: Metallic スロット設定エラー

**症状:**
```
WARNING - Metallic Map slot not available: type object 'FbxSurfaceMaterial' 
  has no attribute 'sMetallic'
```

**原因:**
- FBX SDK の非標準属性（Phong に metallic 定義なし）

**解決:**
- **これは予期される動作**（制限事項）
- Resonite インポート時に CustomProperty で補完
- または Resonite 側で手動設定

### 問題: Alpha 変換失敗

**症状:**
```
ERROR - Failed to create new texture for "mat_grey.dds"
Texture will be use same one.
```

**原因:**
- texconv 実行エラー（パス問題、権限など）

**解決:**
- texconv.exe がインストールされているか確認
- `.tools/TexConv.exe` パスを確認
- ログファイルで詳細エラー確認

---

## 参考資料

### 使用ツール
- **Microsoft DirectXTex (texconv)** - DDS フォーマット変換
  - 公式: https://github.com/microsoft/DirectXTex
  
- **ezTexConv** - チャネルマッピング＋圧縮
  - 参考: https://developer.nvidia.com/texconv

- **FBX SDK** - FBX マテリアル操作
  - 公式: https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2024

### 参考ドキュメント
- [SHADER_TEXTURE_INTEGRATION_GUIDE.md](SHADER_TEXTURE_INTEGRATION_GUIDE.md) - シェーダー/テクスチャマッピング詳細
- [カーモデルインポートワークフロー.md](カーモデルインポートワークフロー.md) - 全体ワークフロー

---

## 付録: フォーマット選択理由

### なぜ BC7 なのか？

**BC7 (BPTC) の特性:**
```
長所:
  - 高品質（BC3/DXT5 より鮮明）
  - アルファ対応（オプション）
  - 幅広い色空間対応
  
短所:
  - エンコード遅い（リアルタイム生成向けでない）
  - BC3 より 50% ファイルサイズ大

AC テクスチャ:
  - 大部分が BC3（DXT5）から変換
  - 品質向上で Resonite 表現改善
```

### なぜ BC5 なのか？

**BC5 (RGTC) の特性:**
```
用途:
  - RG チャネルのみ（BとAは冗長）
  - 法線マップ最適（X,Y = RG, Z = 計算）
  
効果:
  - BC7 比 25% ファイルサイズ削減
  - 圧縮損失小（正規化データ向け）
```

### sRGB vs Linear フォーマット

**sRGB_UNORM (Color):**
```
用途: アルベド、ディティール色
理由: ディスプレイ最適化（ガンマ補正含む）
      テクスチャアーティスト期待値
```

**LINEAR_UNORM (Data):**
```
用途: 法線マップ、メタリックマップ
理由: 物理計算用（線形値のまま）
      補間による品質低下を最小化
```

---

**最終更新:** 2026年2月12日  
**対応バージョン:** Assetonite v1.0 (FBX修正プロセス統合版)
