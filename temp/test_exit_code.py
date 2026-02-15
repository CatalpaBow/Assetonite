import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fbx_fixer.material_fixer import run_material_fix

# Run the material fix
exit_code = run_material_fix(Path(r"F:\Games\SteamGames\steamapps\common\assettocorsa\content\cars\ks_toyota_gt86\fbx"))

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
