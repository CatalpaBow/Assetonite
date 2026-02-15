import sys

import tomllib
from pathlib import Path

from fbx_fixer import run_material_fix

with open('config/.user.toml','rb') as f:
    cfg = tomllib.load(f)
GT86_FBX = Path(cfg['path']['assetto_corsa_fldr']) / 'content' / 'cars' / "ks_toyota_gt86" / "fbx"
exit_code = run_material_fix(GT86_FBX)
sys.exit(exit_code)