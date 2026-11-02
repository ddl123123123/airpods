"""Create a portable source + STL + Pages bundle, without the virtualenv or Git."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
R=Path(__file__).resolve().parents[1]
files=[R/x for x in ['index.html','style.css','viewer.js','README.md','requirements.txt','.nojekyll','.gitignore']]
for folder in ['assets','vendor','models','docs','scripts','.github']:
 files.extend(p for p in (R/folder).rglob('*') if p.is_file() and p.suffix not in ['.log','.pyc','.blend1'] and '__pycache__' not in p.parts)
with ZipFile(R/'beret-airpods-pro3.zip','w',ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,p.relative_to(R))
print(f'Packed {len(files)} files: beret-airpods-pro3.zip')
