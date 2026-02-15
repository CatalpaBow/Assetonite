import sys
from pathlib import Path
import tomllib
# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fbx_fixer.material_fixer import run_material_fix

with open('config/.user.toml','rb') as f:
    cfg = tomllib.load(f)
GT86_FBX = Path(cfg['path']['assetto_corsa_fldr']) / 'content' / 'cars' / "ks_toyota_gt86" / "fbx"

# Run the material fix
exit_code = run_material_fix(GT86_FBX)

print(f"\n===== EXIT CODE RESULT =====")
print(f"Exit code: {exit_code}")
print(f"Status: ", end="")
if exit_code == 0:
    print("SUCCESS - No errors")
elif exit_code == 1:
    print("WARNING - Success with warnings")
elif exit_code == 2:
    print("FAILED - Critical error")
else:
    print(f"Unknown exit code")

sys.exit(exit_code)
