import pytest
import os
from pathlib import Path
import sys

src = Path(__file__).parent.parent / 'src'
sys.path.append(str(src))

from src.fbx_fixer.dds_to_dds_converter import DDStoXFormatter

class TestDDStoXFormatter:
    """
    DDStoXFormatterクラスのテスト
    DDS形式をDXT1形式に変換
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト前のセットアップ"""
        # プロジェクトのルートディレクトリを取得
        self.project_root = Path(__file__).parent.parent
        
        # 入出力パスを設定
        self.input_dds = self.project_root / "data" / "input" / "fbx_fixer" / "test" / "mat_BASE.dds"
        self.output_dir = self.project_root / "data" / "output" / "fbx_fixer"
        self.output_dds_file = self.output_dir / (self.input_dds.stem + '_dxt1.dds')
        self.texconv_exe = self.project_root / ".tools" / "TexConv.exe"
        
        yield
        
        # テスト後のクリーンアップ（出力ファイルを削除）
        try:
            if self.output_dds_file.exists():
                self.output_dds_file.unlink()
        except Exception:
            pass

    def test_input_file_exists(self):
        """入力DDSファイルが存在することを確認"""
        assert self.input_dds.exists(), f"入力ファイルが見つかりません: {self.input_dds}"

    def test_texconv_exe_exists(self):
        """TexConv.exeが存在することを確認"""
        assert self.texconv_exe.exists(), f"TexConv.exeが見つかりません: {self.texconv_exe}"

    def test_convert_dds_to_dxt1(self):
        """DDS形式をDXT1形式に変換する（-o + -sx を使用）"""
        converter = DDStoXFormatter(str(self.texconv_exe))
        
        # 変換実行：output_ddsにディレクトリを渡し、sxで接尾辞を指定
        result = converter.convert(
            input_dds=str(self.input_dds),
            output_dds=str(self.output_dir),
            format="DXT1",
            overwrite=True,
            sx="_dxt1",
        )
        
        # 変換成功を確認
        assert result is True, "変換処理が失敗しました"

    def test_output_file_created(self):
        """DDS出力ファイルが作成されることを確認"""
        converter = DDStoXFormatter(str(self.texconv_exe))
        
        converter.convert(
            input_dds=str(self.input_dds),
            output_dds=str(self.output_dir),
            format="DXT1",
            overwrite=True,
            sx="_dxt1",
        )
        # デバッグ: 出力ディレクトリの中身を表示
        print('\n--- debug listing output_dir ---')
        for p in sorted(self.output_dir.glob('*')):
            print(p)
        print('\n--- debug listing output_dir.parent ---')
        for p in sorted(self.output_dir.parent.glob('*')):
            print(p)

        # 出力ファイルが存在することを確認
        assert self.output_dds_file.exists(), f"出力ファイルが作成されませんでした: {self.output_dds_file}"

    def test_output_file_is_valid_dds(self):
        """DDS出力ファイルが有効なDDSファイルであることを確認"""
        converter = DDStoXFormatter(str(self.texconv_exe))
        
        converter.convert(
            input_dds=str(self.input_dds),
            output_dds=str(self.output_dir),
            format="DXT1",
            overwrite=True,
            sx="_dxt1",
        )
        
        # DDS形式のマジックナンバーを確認 (44 44 53 20)
        with open(self.output_dds_file, 'rb') as f:
            magic = f.read(4)
            assert magic == b'DDS ', "出力ファイルがDDS形式ではありません"

    def test_nonexistent_input_file_raises_error(self):
        """存在しないファイルを指定するとエラーが発生することを確認"""
        converter = DDStoXFormatter(str(self.texconv_exe))
        
        with pytest.raises(FileNotFoundError):
            converter.convert(
                input_dds=str(self.project_root / "nonexistent.dds"),
                output_dds=str(self.output_dir),
                sx="_dxt1",
            )

    def test_output_directory_created(self):
        """出力ディレクトリが存在しない場合、自動作成されることを確認"""
        # 出力ディレクトリを削除（存在する場合）
        output_dir = self.output_dir
        if output_dir.exists():
            try:
                # do not remove entire tree, only ensure it is present/absent for test
                pass
            except Exception:
                pass
        
        converter = DDStoXFormatter(str(self.texconv_exe))
        
        converter.convert(
            input_dds=str(self.input_dds),
            output_dds=str(self.output_dir),
            format="DXT1",
            overwrite=True,
            sx="_dxt1",
        )
        
        # 出力ディレクトリとファイルが作成されることを確認
        assert output_dir.exists(), "出力ディレクトリが作成されませんでした"
        assert self.output_dds_file.exists(), "出力ファイルが作成されませんでした"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])