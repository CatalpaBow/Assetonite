import subprocess
import shlex
import os
from logging import getLogger
logger = getLogger('fix_fbx')

class TexConvWrapper:
    def __init__(self, texconv_path="TexConv.exe"):
        self.texconv_path = texconv_path
        self.inputs = {}
        self.output_file = None
        self.channel_map = {}
        self.options = {}

    def set_output(self, output_path: str):
        self.output_file = output_path
        return self

    def add_input(self, index: int, path: str):
        self.inputs[f"in{index}"] = path
        return self

    def set_channel_map(self, channel: str, mapping: str):
        """
        channel: 'r', 'g', 'b', 'a', 'rgb', 'rgba'
        mapping: e.g., 'in0.rgba', 'in1.r', 'black', 'white'
        """
        self.channel_map[channel] = mapping
        return self

    def set_option(self, key: str, value: str):
        """
        Set general options like:
        - type: '2D', 'Cubemap'
        - compression: 'none', 'medium', 'high'
        - usage: 'Color', 'Linear', 'HDR', 'NormalMap'
        - mipmaps: 'none', 'Linear'
        """
        self.options[key] = value
        return self

    def build_command(self):
        if not self.output_file:
            raise ValueError("Output file path is not set.")

        cmd = [self.texconv_path, "-out", self.output_file]

        # Input images
        for key, path in self.inputs.items():
            cmd += [f"-{key}", path]

        # Channel mappings
        for channel, mapping in self.channel_map.items():
            cmd += [f"-{channel}", mapping]

        # Other options
        for opt, val in self.options.items():
            cmd += [f"-{opt}", val]

        return cmd

    def run(self, verbose=True):
        cmd = self.build_command()

        if verbose:
            cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
            text = f"Running ezTexConv: {cmd_str}"
            logger.info(text)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"TexConv failed with code {result.returncode}. Outputlog:{result.stdout}")
        else:
            if verbose:
                logger.debug(result.stdout)

        return result


# -------------------------------
# ✅ 使用例
# -------------------------------
if __name__ == "__main__":
    '''
    conv = TexConvWrapper(r"D:\Devlop\Assetonite\.tools\ezTexConv.exe")  # 正しいパスに変更

    conv.set_output(r"D:\Devlop\Assetonite\.tools\interior_rslt.dds")\
        .add_input(0, r"D:\Devlop\Assetonite\.tools\interior_lod0.dds")\
        .set_channel_map("rgba", "in0")\
        .set_option("usage", "color")\
        .run()
    '''