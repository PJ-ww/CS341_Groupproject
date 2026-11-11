"""Build orchestration/dist/cs341_pipeline.zip for the 5 Lambda functions.

Run from the project root:   python orchestration/build_package.py
The zip contains lambda_handlers.py + ingestion/config.py + ingestion/validate_data.py
+ transformation/scripts/*.py  (no data, no output files -> a few KB).
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "orchestration" / "dist"
DIST.mkdir(parents=True, exist_ok=True)
target = DIST / "cs341_pipeline.zip"

files = [(ROOT / "orchestration" / "lambda_handlers.py", "lambda_handlers.py"),
         (ROOT / "ingestion" / "config.py", "ingestion/config.py"),
         (ROOT / "ingestion" / "validate_data.py", "ingestion/validate_data.py")]
files += [(p, f"transformation/scripts/{p.name}") for p in sorted((ROOT / "transformation" / "scripts").glob("*.py"))]

with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
    for src, arc in files:
        if not src.exists():
            raise SystemExit(f"missing file: {src}")
        zf.write(src, arc)
print(f"built {target}  ({target.stat().st_size / 1024:.1f} KB, {len(files)} files)")