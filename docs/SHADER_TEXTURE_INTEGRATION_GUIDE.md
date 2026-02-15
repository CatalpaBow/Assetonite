# AssettoCorsaSim シェーダー＆テクスチャ統合ガイド

**統合日**: 2026-02-12  
**ソース**: docs/ 内の複数ドキュメント統合版  
**対象**: Assetonite FBX 処理パイプライン

---

## 📑 目次

1. [シェーダー体系](#シェーダー体系)
2. [テクスチャスロット一覧](#テクスチャスロット一覧)
3. [アルファチャネルの使用方法](#アルファチャネルの使用方法)
4. [テクスチャ詳細マップ](#テクスチャ詳細マップ)
5. [チュートリアル・実装例](#チュートリアルロジック)
6. [Resonite 互換性](#resonite-互換性テクスチャ変換)
7. [Assetonite での実装](#assetonite-での実装)

---

## シェーダー体系

### 総数: 78 シェーダー
- **有効**: 52 シェーダー  
- **無効（エディタで非表示）**: 26 シェーダー

### シェーダー分類

#### 🌍 Ground Shaders
地表/アスファルト/砂などに使用

| シェーダー名 | テクスチャスロット | 用途 |
|------------|------------------|------|
| **ksIdealLine** | txDiffuse | レーシングラインの白線 |
| **ksSkidMark** | txDiffuse | タイヤスキッドマーク |

#### 🌳 Object Shaders  
樹木/草/建築物など

| シェーダー名 | テクスチャスロット | 用途 |
|------------|------------------|------|
| **ksGrass** | txDiffuse, txVariation | 草地（色の変動対応） |
| **ksFlags** | txDiffuse | 旗・フラグ |
| **ksTree** | txDiffuse | 樹木（良好なフィルタリング） |

#### 🌤️ Sky / Air Shaders
空・大気エフェクト

| シェーダー名 | テクスチャスロット | 用途 |
|------------|------------------|------|
| **ksSky** | — | (単色空) |
| **ksSkyBox** | — | (キューブマップスロット) |
| **ksSkyCubemap** | — | キューブマップ空 |
| **ksClouds** | txDiffuse | クラウドレイヤー |
| **ksPostFOG** | txDiffuse, txDepth | ポストプロセス フォグ |
| **ksPostFOG_MS** | txDiffuse, txDepth | マルチサンプル フォグ |

#### 🏎️ Car Shaders
車のメインシェーダー

| シェーダー名 | テクスチャスロット | 特性 |
|------------|------------------|------|
| **ksCarPaintSimple** | txDiffuse | シンプル塗装（Diffuse のみ） |
| **ksTyres** | txDiffuse, txNormal, txDirty, txBlur, txNormalBlur | タイヤ（グリップマーク対応） |
| **newStefano_ksTyres** | txDiffuse, txNormal | 改良版タイヤシェーダー |
| **ksBrakeDisc** | txDiffuse, txNormal, txGlow, txBlur, txNormalBlur | ブレーキディスク（高温発光） |
| **ksBrokenGlass** | txDiffuse, txNormal | 割れたガラス |
| **ksWindscreen** | txDiffuse | ウィンドスクリーン（污れ、水滴） |
| **ksCircularRPM** | txDiffuse, txDiffuseON | メーター・RPMゲージ（2フレーム） |

#### 🔀 Multiple Use Shaders
汎用（トラック/車両両用）

##### PerPixel 系
最も汎用的なシェーダーファミリー

```
ksPerPixel              — 基本的な1層テクスチャ
ksPerPixel_dual_layer   — 2層レイアウト
ksPerPixel_nosdw        — 影なし版
ksPerPixelAlpha         — 透明度制御可能
ksPerPixelReflection    — 反射対応
ksPerPixelSimpleRefl    — シンプル反射
```

##### PerPixel + Alpha Test 系
透明性処理をテストモード

```
ksPerPixelAT            — Alpha Test（ON/OFF のみ）
ksPerPixelAT_NM         — AT + 法線マップ
ksPerPixelAT_NS         — AT + No Shadow
```

##### PerPixel + Normal Map 系
法線マップ対応

```
ksPerPixelNM            — 基本法線マップ
ksPerPixelNM_UV2        — セカンダリ UV チャネル
ksPerPixelNM_UVMult     — UV スケーリング
```

##### PerPixelMultiMap 系
**最も複雑・多機能族**

```
ksPerPixelMultiMap                  — 基本（Diffuse + Normal + Maps + Detail）
ksPerPixelMultiMap_AT               — + Alpha Test
ksPerPixelMultiMap_AT_NMDetail      — AT + 詳細法線マップ
ksPerPixelMultiMap_damage           — ダメージマップ対応
ksPerPixelMultiMap_damage_dirt      — ダメージ + ダスト層
                                      (最フル機能)
ksPerPixelMultiMap_NMDetail         — 詳細法線マップ版
ksPerPixelMultiMapSimpleRefl        — 反射簡略版
```

**ksPerPixelMultiMap_damage_dirt (最複雑な例)**
- txDiffuse: 基本色（Alpha: 詳細マップの適用範囲）
- txNormal: 法線マップ (DirectX 規格)
- txMaps: PBR パック（R=粗さ, G=反射鋭さ, B=AO）
- txDetail: 詳細マップ（金属フレークなど）
  - Color: 実際の色
  - **Alpha チャネルが重要**: 明るい→スペキュラ鋭い、暗い→スペキュラ鈍い
- txDamage: ダメージテクスチャ（傷、剥離）
- txDust: ダスト層（埃、汚れ）
- txDamageMask: ダメージ適用範囲マスク

##### MultiLayer 系
複数の詳細レイヤー（高度な装飾向け）

```
ksMultilayer            — RGBA 4層分解
ksMultilayer_fresnel_nm — + フレネル + 法線マップ
ksMultilayer_objsp      — オブジェクト空間投影
```

#### 🔧 Other / Misc Shaders

| シェーダー名 | テクスチャスロット | 用途 |
|------------|------------------|------|
| **ksOrenNayar** | txDiffuse | 布や粗い面（Oren-Nayar 反射） |
| **ksSimpleShader** | txDiffuse | 非常にシンプル |
| **ksSkinnedMesh** | txDiffuse, txNormal, txMaps, txDetail | スキンメッシュ用 |
| **ksSkinnedMesh_NMDetaill** | + txNormalDetail | スキン + 詳細法線 |

#### 📵 Disabled Shaders (参考)
エディタで非表示化されているが、`shader_filter_list.txt` で有効化可

```
GLTextured, ksCameraDirt, ksFont, ksFXAA (x6), ksHighPass, 
ksParticle, ksPostAdaptLum, ksPostBlur*, ksPostBW, 
ksPostCopy, ksPostToneMap, ksSelectedMesh, ksShadowGen*, ...
```

---

## テクスチャスロット一覧

### 標準スロット

| スロット名 | 形式 | 用途 |
|-----------|------|------|
| **txDiffuse** | RGB(DA) | ベースカラー (+ Alpha: 透明度/マスク) |
| **txNormal** | RGB (DirectX) | 法線マップ (+ Alpha: 用途依存) |
| **txMaps** | RGB | PBR パック情報 |
| **txDetail** | RGB | 詳細マップ (+ Alpha: 鋭さ/反射)|
| **txDamage** | RGB | ダメージ表現 |
| **txDust** | RGB | ダスト/汚れ |
| **txDamageMask** | GS or A | ダメージ適用範囲 |
| **txGlow** | RGB | 発光マップ（ブレーキ等） |

### 高度なスロット

| スロット名 | 用途 |
|-----------|------|
| **txVariation** | テクスチャ色のバリエーション (grass) |
| **txLayer1** / **txLayer1_Mask** | 2層ブレンド用 |
| **txDetailR/G/B/A** | MultiLayer の4層分解 |
| **txDetailNM** | Detail 用の法線マップ |
| **txNormalDetail** | 詳細法線（MultiMap_NMDetail） |
| **txDirty** | ダーティレイヤー (タイヤ等) |
| **txBlur** | ブラーレイヤー（high-speed感） |
| **txNormalBlur** | Blur の法線 |
| **txMask** | MultiLayer マスク |
| **txDepth** | デプスマップ（PostFOG） |

### 圧縮推奨フォーマット

| テクスチャタイプ | 推奨フォーマット | 理由 |
|-----------------|-----------------|------|
| Diffuse (no alpha) | DXT1 | 圧縮率高い |
| Diffuse (with alpha) | DXT5 / BC3 | Alpha チャネル保持 |
| Normal Map | BC5 / BC4 | 高品質法線 |
| Grayscale | DXT1 | 圧縮率最高 |
| Color Detail | DXT5 | Color + Alpha |
| **R8G8_UNORM (AC標準)** | **BC7 (RGBA)** | **Resonite互換性のため** |

#### ⚠️ R8G8_UNORM フォーマットに関する重要な注意

AC では txDiffuse などで **R8G8_UNORM** が使用されます：
- **R8 チャネル**: グレースケール値（AO など）
- **G8 チャネル**: アルファチャネル情報

**Resonite との互換性問題**:
- ❌ Resonite は R8G8_UNORM を正常にインポートできない
- ✅ **解決策**: BC7 (RGBA) に変換して使用
  - BC7 は高品質圧縮で RGB グレースケール + Alpha チャネルを最適に保持
  - BC5 (RG) は容量効率が良いが、Resonite でグレースケール扱いできない
  - **推奨**: RGBA の BC7 フォーマットで統一

**Assetonite での処理**:
```
R8G8_UNORM (AC用)
    ↓ (texture_integrator.py で変換)
BC7 with R→RGB, G→A
    ↓
Resonite へエクスポート
```

---

## アルファチャネルの使用方法

### ⚠️ 重要: シェーダーごとに異なる！

#### 1️⃣ 大多数のシェーダー (ksPerPixel*, ksPerPixelReflection など)

**txDiffuse の Alpha チャネル = 透明度**

```
BlendMode = 0 (eOpaque)    → Alpha は無視
BlendMode = 1 (eAlpha)     → Alpha で透明度制御
```

**INI での指定**:
```ini
[MATERIAL_0]
NAME=Material_Name
ALPHABLEND=0          ; 0 = Opaque (デフォルト, Alpha 無視)
ALPHABLEND=1          ; 1 = Alpha ( Diffuse.Alpha で透明度制御)
ALPHATEST=0           ; 0 = False (Alpha Test 無効)
ALPHATEST=1           ; 1 = True  (Alpha Test 有効)
```

⚡ **パフォーマンス注意**: 透明ブレンド (ALPHABLEND=1) は Z バッファの問題あり  
→ 可能なら Alpha Test (ALPHATEST=1) を使用

---

#### 2️⃣ NM 系シェーダー (ksPerPixelNM*, ksPerPixelAT_NM)

**txDiffuse の Alpha チャネル = 無視される**  
**txNormal の Alpha チャネル = 実際のマスク/透明度**

```
用途:
- テクスチャの色化が容易 (skin tone など)
- Alpha テストにも使用可
```

**例**: RX-7 ビッグウィング
- txNormal Alpha: 8×8 テクスチャ 1 枚でストライプ効果とリムの色化を同時実現

---

#### 3️⃣ MultiMap 系 (ksPerPixelMultiMap*)

**txDiffuse の Alpha チャネル = Detail マップの適用範囲マスク**

```
Black (Alpha = 0)   → Detail マップの効果 ON
White (Alpha = 255) → Detail マップの効果 OFF
Gray (Alpha = 128)  → 50% 適用
```

**txDetail の Alpha チャネル = スペキュラ/反射 鋭さ**

```
Black (Alpha = 0)   → スペキュラ鈍い (ksSpecularEXP 大)
White (Alpha = 255) → スペキュラ鋭い (ksSpecularEXP 小)i
```

🎨 **使用例: 金属フレーク効果**
- detail texture: 金属フレークの色  
- detail texture alpha: 部分的に白（フレークの位置）

---

#### 4️⃣ Alpha Test シェーダー (ksPerPixelAT, ksPerPixelAT_*)

**txDiffuse の Alpha チャネル = ON/OFF マスク**

```
Alpha >= AlphaRef   → ピクセル描画
Alpha < AlphaRef    → 描画スキップ
```

⚡ **特徴**: Z バッファ問題なし（推奨）  
⚠️ **注意**: AlphaRef は固定（調整不可）

---

#### 5️⃣ 特殊: ksTyres, ksBrakeDisc

**txDiffuse の Alpha チャネル = スペキュラ＆反射レベルコントロール**

```
Alpha = 0   → 反射・スペキュラなし
Alpha = 255 → 最大反射・スペキュラ

用途: ブレーキディスクの穴、タイヤの磨耗表現
```

---

#### 6️⃣ 特殊: ksPerPixelMultiMap_AT

**複合型: MultiMap + AT の両方の特性**

```
txDiffuse Alpha   = Detail 適用範囲 AND Alpha テストしきい値
txNormal Alpha    = AT マスク (NM シェーダーのように)
txDetail Alpha    = スペキュラ鋭さ
```

😲 **これだけで複数の効果を実現可能！**

---

## テクスチャ詳細マップ

### txMaps (Assetto Corsa) チャネル割り当て

**標準割当**:
```
R チャネル = Roughness (粗さ)
  0   → 鏡面反射 (ピカピカ)
  255 → マット (艶消し)

G チャネル = Reflection sharpness (反射鋭さ)
  別名: "green channel controls both reflection and specular sharpness"
  0   → 反射ぼやけ
  255 → 反射鋭い

B チャネル = Reflection Brightness
  0   → 
  255 → 
```

**影響するシェーダープロパティ**:

| プロパティ | 型 | 範囲 | 例 |
|-----------|-----|------|-------|
| **isAdditive** | int | 0, 1, 2 | 反射ブレンドモード |
| **ksSpecularEXP** | float | 1-255 | スペキュラ鋭さ指数 |
| **ksSpecular** | float | | スペキュラ強度 |

---

### Reflection Modes: isAdditive パラメータ

```
isAdditive = 0  (Fresnel Mix - 標準)
├─ 透過率が角度依存（フレネル効果）
├─ 最大反射鋭さは ksSpecularEXP = 255 必須
└─ 用途: プラスチック、ゴム、ペイント、etc.

isAdditive = 1  (Additive - ガラス等)
├─ 反射を加算合成
├─ ks SpecularEXP = 255 で鋭い反射
└─ 用途: ガラス、透明素材

isAdditive = 2  (Clearcoat - クリアコート)
├─ 反射はほぼ常に鋭い (SkSpecularEXP >= 8 で十分)
├─ Fresnel Mix に戻る
└─ 用途: 塗装上のクリアコート層、透明コーティング
```

---

### Glossiness / Reflection の調整（実務メモ）

車体の見た目（光沢感・反射の鋭さ・明るさ）は `txMaps` の各チャネルとマテリアルパラメータで細かく制御できます。実務的には下記を順に調整します。

- `txMaps` チャネルの役割（再掲）:
  - **R チャネル** = Specular brightness（スペキュラ強度、スポットの明るさ）
  - **G チャネル** = Reflection/specular sharpness（反射の鋭さ／スペキュラの拡散度）
  - **B チャネル** = Reflection brightness（反射全体の明るさ）

- 標準の使い方（'standard'）:
  - AO を `R` / `B` に入れ、`G` を白にする（初期状態として反射鋭さを固定しない設定）

- 主要マテリアルパラメータ:
  - `ksSpecular` — スポット（鏡面）明るさ（強度）
  - `ksSpecularEXP` — スペキュラスポットのサイズと反射鋭さ（値が大きいほどスポットは小さく鋭くなる）
  - `isAdditive` — 反射合成モード（0: Fresnel mix、1: Additive、2: Clearcoat のような鋭い反射）
    - `isAdditive = 2` の場合、`ksSpecularEXP` に大きな乗数が適用され、非常に鋭い反射になる挙動が報告されています。

- 実務的な調整手順:
  1. CM Showroom で車体（Car body）を選び、`txMaps` を確認・編集して R/G/B の影響を観察。
  2. 反射が不足する場合は `ksSpecular` / `ksSpecularEXP` を調整して基点を変更。
  3. さらに見た目を変えたい場合は CSP のマテリアルテンプレートを編集 (path: `assettocorsa/extension/config/cars/common`)。
     - CSP テンプレートで `ksSpecular`, `ksSpecularEXP`, `isAdditive` を上書きして配布可能。
  4. テクスチャは Resonite 互換（BC7 等）に変換してから確認する。

- まとめ: 見た目を大きく変えたいときは `txMaps`（R/G/B）で基本挙動を作り、`ksSpecular` / `ksSpecularEXP` / `isAdditive` で微調整、必要に応じ CSP テンプレートで恒久変更。

### Specular 用語の解説と仕上がり調整ガイド

以下は実務でよく混乱する用語の定義と、`txMaps` / マテリアルパラメータを使った具体的な調整手順です。

用語定義:
- **Specular intensity（スペキュラ強度／中心の明るさ）**: ハイライトの中心点での輝度。`ksSpecular` や `txMaps` の R チャネルで制御されることが多い。
- **Specular sharpness（スペキュラ鋭さ）**: ハイライトの鋭さ（スポットの“広がり”）。`ksSpecularEXP` によって制御され、値が大きいほどスポットは**小さく鋭く**なる（＝見かけ上「シャープ」）。
- **Reflection intensity（反射明るさ）**: 面全体に対する反射の明るさ（鏡面以外の反射成分）。`txMaps` の B チャネルやマテリアルの乗算で調整。

注意点（マップのチャネル割当はプロジェクトや mod により差がある）:
- フォーラム実例: `txMaps` の **R=specular brightness, G=reflection sharpness, B=reflection brightness** という運用がよく見られます。
- 一方で別のガイドでは `R=roughness, G=reflection sharpness, B=AO` のように使う場合もあり、プロジェクト固有の慣習に従う必要があります。

仕上がり別の調整方針:
- **Metallic（メタリック）**
  - 目標: 小さく鋭い、明るいハイライト
  - やること: `ksSpecular` を上げ（強度）、`ksSpecularEXP` を高めに設定（スポットを小さく鋭くする）、`txMaps.G` を高く（反射鋭さ）・`txMaps.R` を高め（スペキュラ強度）に設定。反射全体は `txMaps.B` で補正。
- **Matte（マット）**
  - 目標: 広く柔らかい、暗めのハイライト（ほとんど拡散）
  - やること: `ksSpecular` を低め、`ksSpecularEXP` を低く（スポットを大きくソフトに）、`txMaps.G` を低く（反射をぼかす）、`txMaps.B` を低めに。
- **Satin（サテン）**
  - 目標: 明るめだが柔らかいハイライト（光沢はあるが拡散が強い）
  - やること: `ksSpecular` を中〜高に、`ksSpecularEXP` は低めから中程度に（シャープさは控えめ）、`txMaps.G` は中程度、`txMaps.B` をやや高めに設定。

実務ヒント:
- CM Showroom でパーツを選びつつ `txMaps` を直接差し替えて R/G/B の影響を視覚で確認する。小さな差でも `ksSpecularEXP` の変化は見た目に大きく出ます。
- `isAdditive` の設定により反射の合成方式が変わるため、同じマップでも見た目が大きく異なる。必要なら CSP テンプレートで `isAdditive` を変えて試す。
- txDetail の Alpha がスペキュラ鋭さに影響するケースもある（MultiMap 系）。細かいフレーク表現は detail alpha を使って調整。

おすすめのワークフロー:
1. まず `txMaps`（R/G/B）を編集してベース特性を作る（プレビューで確認）。
2. `ksSpecular` と `ksSpecularEXP` で望むスポットの明るさと鋭さに合わせる。
3. `isAdditive` を切り替えて合成挙動を確認（ガラス風やクリアコート表現など）。
4. `txDetail` の alpha を用いて部分的なスペキュラ鋭さを追加する（フレーク等）。

これらの操作を組み合わせて、iRacing と同程度の細かい仕上がりに近づけられますが、チャネル割当の差やレンダラー差により微調整は必須です。


### 詳細マップ (txDetail) の実装パターン

#### パターン A: 車体ペイント用

```
MainDiffuse = AO テクスチャ (全て Black Alpha)
  ↓
Detail = 実際の塗装色 (Red, White, Blue など)
  ├─ Color: 金属フレーク、炭素繊維パターン
  ├─ Alpha: フレークの鋭さマップ（部分的に白）
  └─ Result: Black Alpha × Color = Color (Multiply)

効果:
- 1 つの AO テクスチャ + 複数の Detail テクスチャで色替え対応
- メモリ効率化
- ストリートカーの色替バリエーション対応
```

#### パターン B: トラック路面用 (MultiLayer)

```
主テクスチャ = アスファルト基本
Detail (Projected from Above) = 舗装パターン、草地パターン
  
特性: オブジェクト空間ではなく、上からの投影
→ 垂直なオブジェクト（壁）には不向き
```

#### パターン C: ダメージ表現 (damage_dirt)

```
BaseDiffuse = 新車状態の塗装
txDamage = 傷・塗装剥離・汚れ
txDamageMask = ダメージの適用範囲

レンダリング:
output = lerp(BaseDiffuse, txDamage, txDamageMask.alpha)
```

---

## チュートリアル：ロジック

### ❓ なぜ Detail マップが見えないのか？

**よくある質問**（`How to use txDetail...` より）

```
設定:
- Shader: ksPerPixelMultiMap
- txDiffuse: グレー
- txDetail: チェッカーパターン
- useDetail = 1
- detailUVMultiplier = 1

問題: Detail が見えない
```

**答え**:

```
1. DDS フォーマット必須！
   ✗ PNG
   ✓ DXT1/5, BC1/3

2. txDiffuse は Alpha チャネルが重要
   ✗ Alpha = 白 (または削除)
   ✓ Alpha = 黒 (フル Detail 適用)
   
   ロジック: Detail = Diffuse.RGB * (1 - Diffuse.Alpha) + Detail.RGB * Diffuse.Alpha

3. txDiffuse は DXT5 / BC3 で保存
   (Alpha チャネルを保持するため)

4. Detail テクスチャがグレースケール以外でも OK
   - カラー OK
   - Alpha チャネルが実際の効果 (鋭さ)
```

---

## Resonite 互換性・テクスチャ変換

### 問題の背景

AC で使用される **R8G8_UNORM** フォーマットは Resonite で正常にインポートできません。  
Assetonite はこれを BC7 (RGBA) に変換して対応します。

### 変換戦略

#### ステップ 1: R8G8_UNORM の解釈

```
R8G8_UNORM テクスチャ:
  R8 チャネル (Red)   → グレースケール値 (AO, Metallic など)
  G8 チャネル (Green) → アルファチャネル (透明度, マスク)
```

#### ステップ 2: BC7 (RGBA) への変換

```
R8G8_UNORM
    ↓
BC7 (RGBA):
  R チャネル = R8 の値 × 255
  
  G チャネル = R8 の値 × 255 (グレースケールとして複製)
  
  B チャネル = R8 の値 × 255 (グレースケールとして複製)
  
  A チャネル = G8 の値 (Alpha 情報)
```

**理由**:
- ✅ Resonite で正常にインポート可能
- ✅ RGB をグレースケール として扱える
- ✅ Alpha チャネルを保持
- ✅ BC7 は高品質圧縮（BC3 より画質が向上）

#### ステップ 3: 処理フロー

```
AC INI
  ├─ RES_txMaps_TEXTURE=material_maps.dds (R8G8_UNORM)
  └─ RES_txDiffuse_TEXTURE=material_d.dds

↓ cfg_materials.py (テクスチャパス抽出)

↓ texture_processor.py (シェーダー分析)

↓ pbr_material_applier.py (FBX 適用)

↓ texture_integrator.py (フォーマット変換)
  ├─ DDS を読み込み
  ├─ R8G8_UNORM → BC7 変換
  └─ data/output/converted/ へ出力

↓ export FBX
  └─ テクスチャ: material_maps_BC7.dds

↓ Resonite へインポート ✅
```

### 実装責務

| モジュール | 責務 |
|-----------|------|
| **texture_integrator.py** | R8G8_UNORM 検出・BC7 変換・出力 |
| **pbr_material_applier.py** | 変換後のテクスチャパスを FBX にリンク |
| **material_fixer.py** | output テクスチャプール管理 |

---

## Assetonite での実装

### データフロー

```
INI ファイル (cfg_materials.py が読込)
  ├─ シェーダー名 (e.g., "ksPerPixelMultiMap_damage_dirt")
  ├─ テクスチャパス (txDiffuse, txNormal, ...)
  └─ PBR パラメータ (Roughness, Metallic, ...)

↓ texture_processor.py

ShaderProfiler:
  └─ シェーダー分析
      ├─ category 判定
      ├─ required_textures 検出
      ├─ Alpha チャネル挙動 判定
      └─ ShaderProfile 生成

TextureDetector:
  └─ テクスチャマッピング
      ├─ Shader-aware lookup
      ├─ Pattern fallback
      └─ TextureMapping 生成

TextureProcessor:
  └─ 操作計画生成
      ├─ 欠落テクスチャ検出
      ├─ PBR 結合計画
      ├─ チャネル処理計画
      └─ operations dict 生成

↓ pbr_material_applier.py (FBX SDK)

└─ FBX マテリアルに適用

↓ texture_integrator.py (新規実装予定)

├─ DDS チャネル操作
├─ PBR 結合
├─ 法線正規化  
└─ 最終テクスチャ生成
```

### 実装チェックリスト

- [x] `texture_processor.py`: シェーダー・テクスチャマッピング
- [x] Alpha チャネルフラグ実装
- [ ] `pbr_material_applier.py`: FBX SDK 統合
- [ ] `texture_integrator.py`: DDS 操作・結合
- [ ] **R8G8_UNORM → BC7 変換機能** (Resonite 互換性)
- [ ] 統合テスト

---

## 参考資料

### AC フォーラムスレッド
- Track Materials / Shaders: http://www.assettocorsa.net/forum/index.php?threads/track-materials-shaders.10174/
- Car materials / shaders / modelling stuff: http://www.assettocorsa.net/forum/index.php?threads/...odelling-stuff...
- Proper technique in track making + tips: http://www.assettocorsa.net/forum/index.php?threads/...

### ドキュメント ソース
- `Assetto Corsa Shaders, Texture maps list.txt` — シェーダー・テクスチャ完全リスト
- `About Alpha-channel.txt` — Alpha チャネル仕様ガイド
- `Car materials shaders modelling stuff.txt` — 反射・Additive パラメータ
- `How to use txDetail with ksPerPixelMultiMap.txt` — Detail マップ Q&A

---

**ドキュメント統合版**  
*Assetonite PBR テクスチャパイプライン向けに最適化*
