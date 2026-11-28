"""Build orchestration/dist/cs341_pipeline.zip for the 7 Lambda functions.

Run from the project root:   python orchestration/build_package.py
The zip contains lambda_handlers.py + ingestion/config.py + ingestion/validate_data.py
+ the current Chiang Mai transformation scripts + storage/ scripts used by CurateBatch
and QueryBatch + the curated SQL files (no data/output files).
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
# CurateBatch runs build_curated.py; QueryBatch imports run_athena.py (both import schema.py)
files += [(ROOT / "storage" / n, f"storage/{n}") for n in ("schema.py", "build_curated.py", "run_athena.py")]
files += [(p, p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / "sql" / "curated").rglob("*.sql"))]

with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
    for src, arc in files:
        if not src.exists():
            raise SystemExit(f"missing file: {src}")
        zf.write(src, arc)
print(f"built {target}  ({target.stat().st_size / 1024:.1f} KB, {len(files)} files)")
