import subprocess
import shlex
import os
from pathlib import Path
from logging import getLogger

logger = getLogger('fix_fbx')


class DDStoXFormatter:
    """
    Microsoft TexConvラッパークラス
    DDS形式のテクスチャをDXT1形式に変換します
    """

    def __init__(self, texconv_path: str = None):
        """
        Args:
            texconv_path: TexConv.exeの完全パスまたは相対パス
                         Noneの場合は、このモジュールを基準に自動検出
        """
        if texconv_path is None:
            # このモジュールの位置から.tools/TexConv.exeへの絶対パスを構築
            module_dir = Path(__file__).parent.parent.parent  # src/fbx_fixer -> src -> project_root
            texconv_path = str(module_dir / ".tools" / "TexConv.exe")
        
        self.texconv_path = texconv_path

    def convert(self, input_dds: str, output_dds: str, format: str = "DXT1", overwrite: bool = True, sx: str | None = None) -> bool:
        """
        DDS形式のファイルを指定されたフォーマットに変換します

        Args:
            input_dds: 入力DDSファイルのパス
            output_dds: 出力DDSファイルのパス
            format: 出力フォーマット（デフォルト: "DXT1"）
            overwrite: 既存ファイルを上書きするか（デフォルト: True）

        Returns:
            bool: 変換成功時True、失敗時False

        Raises:
            FileNotFoundError: 入力ファイルが見つからない場合
            RuntimeError: TexConv実行エラー
        """
        need_rename = False
        # 入力ファイルの存在確認
        input_path = Path(input_dds)
        if not input_path.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_dds}")

        # 出力ディレクトリを決定（output_ddsはディレクトリでもファイルパスでも受け付ける）
        output_path = Path(output_dds)
        # 指定が既存のディレクトリ、またはパス末尾が区切り文字でディレクトリ指定に見える場合はそのままディレクトリ扱い
        if output_path.exists() and output_path.is_dir():
            output_dir = output_path
        elif str(output_dds).endswith(('/', '\\')):
            output_dir = output_path
        else:
            # 出力パスがファイル(hoge.dds)の場合、出力後のファイルのリネームが必要
            output_dir = output_path.parent
            need_rename = True
        # 出力ディレクトリの作成
        output_dir.mkdir(parents=True, exist_ok=True)

        # コマンド構築（-oオプションで出力ディレクトリを指定）
        cmd = [
            self.texconv_path,
            "-r",
            str(input_path),
            "-ft",
            "dds",
            "-f",
            format,
            "-o",
            str(output_dir),
        ]

        # -sx オプションが指定されていれば追加（接尾辞はファイル名の末尾に挿入されます）
        if sx:
            # TexConv expects the suffix string (例: _dxt1)
            cmd += ["-sx", str(sx)]

        # 上書きフラグ
        if overwrite:
            cmd.append("-y")

        # ログ出力（コマンド表示）
        cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
        logger.info(f"実行: {cmd_str}")
        logger.info(f"出力先: {output_dds}")

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
            # 出力ファイルのリネーム
            if need_rename:
                output_file_path = output_dir / input_path.with_suffix(".dds").name
                new_path = output_file_path.with_name(output_path.stem + ".dds")
                output_file_path.rename(new_path)
                logger.info(f"Rename output file {input_path.name} -> {output_path.stem + '.dds'}")
            # 成功ログ
            logger.debug(result.stdout)
            logger.info(f"変換成功: {input_dds} -> {output_dds} (フォーマット: {format})")

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
        converter = DDStoXFormatter()
        converter.convert(
            input_dds=r"D:\path\to\dds\texture.dds",
            output_dds=r"D:\path\to\output\texture.dds",
            format="DXT1"
        )
        print("✓ 変換完了")
    except Exception as e:
        print(f"✗ エラー: {e}")
