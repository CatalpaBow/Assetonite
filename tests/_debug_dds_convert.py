from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.fbx_fixer.dds_to_dds_converter import DDStoXFormatter

project_root = Path(__file__).parent.parent
input_dds = project_root / 'data' / 'input' / 'fbx_fixer' / 'test' / 'mat_BASE.dds'
output_dir = project_root / 'data' / 'output' / 'fbx_fixer'

print('input_dds:', input_dds)
print('output_dir:', output_dir)

conv = DDStoXFormatter(str(project_root / '.tools' / 'TexConv.exe'))
try:
    conv.convert(str(input_dds), str(output_dir), format='DXT1', overwrite=True, sx='_dxt1')
    print('convert returned')
except Exception as e:
    print('convert raised', e)

print('\nListing output_dir:')
for p in sorted(output_dir.glob('*')):
    print(p)

print('\nListing output_dir.parent:')
for p in sorted(output_dir.parent.glob('*')):
    print(p)
