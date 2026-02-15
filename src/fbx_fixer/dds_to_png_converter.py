import subprocess
import shlex
import os
from pathlib import Path
from logging import getLogger

logger = getLogger('fix_fbx')


class DDStoPNGConverter:
    """
    Microsoft TexConvラッパークラス
    R8G8_UNORM形式のDDSファイルをPNG形式に変換します
    """

    def __init__(self, texconv_path: str = "../.tools/TexConv.exe"):
        """
        Args:
            texconv_path: TexConv.exeの相対パス（デフォルト: ../.tools/TexConv.exe）
                         実行時のカレントディレクトリがsrcフォルダであることを想定
        """
        self.texconv_path = texconv_path

    def convert(self, input_dds: str, output_png: str, overwrite: bool = True) -> bool:
        """
        DDS形式のファイルをPNG形式に変換します

        Args:
            input_dds: 入力DDSファイルのパス
            output_png: 出力PNGファイルのパス
            overwrite: 既存ファイルを上書きするか（デフォルト: True）

        Returns:
            bool: 変換成功時True、失敗時False

        Raises:
            FileNotFoundError: 入力ファイルが見つからない場合
            RuntimeError: TexConv実行エラー
        """
        # 入力ファイルの存在確認
        input_path = Path(input_dds)
        if not input_path.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_dds}")

        # 出力ディレクトリの作成
        output_path = Path(output_png)
        output_path.parent.mkdir(parents=True, exist_ok=True) 

        # コマンド構築
        cmd = [
            self.texconv_path,
            "-r",
            str(input_path),
            "-ft",
            "png",
        ]

        # 上書きフラグ
        if overwrite:
            cmd.append("-y")

        # ログ出力（コマンド表示）
        cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
        logger.info(f"実行: {cmd_str}")
        logger.info(f"出力先: {output_png}")

        try:
            # TexConv実行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                error_msg = f"TexConv実行エラー (コード: {result.returncode})\n{result.stdout}\n{result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # 成功ログ
            logger.debug(result.stdout)
            logger.info(f"変換成功: {input_dds} -> {output_png}")

            # 出力ファイルの実際の出力場所を確認
            # TexConvはデフォルトで入力ファイルと同じディレクトリに出力するため、
            # 必要に応じてファイルを移動
            expected_output = input_path.parent / output_path.name
            if expected_output.exists() and str(expected_output) != output_png:
                expected_output.rename(output_path)
                logger.debug(f"出力ファイル移動: {expected_output} -> {output_png}")

            return True

        except Exception as e:
            logger.error(f"変換処理中にエラーが発生しました: {str(e)}")
            raise


# ================================
# 使用例
# ================================
if __name__ == "__main__":
    import logging
    from src.utils.logger_getter import get_logger

    logger = get_logger('fix_fbx')

    try:
        # デフォルトパスを使用（実行時のカレントディレクトリはsrc）
        converter = DDStoPNGConverter()
        converter.convert(
            input_dds=r"D:\path\to\dds\texture.dds",
            output_png=r"D:\path\to\png\texture.png"
        )
        print("✓ 変換完了")
    except Exception as e:
        print(f"✗ エラー: {e}")
