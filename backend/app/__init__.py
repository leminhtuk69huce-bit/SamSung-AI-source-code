# AI OCR CCCD/CMND System — App Package
import os
import sys
import tempfile
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ["PYTHONIOENCODING"] = "utf-8"

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")


# Fix Windows temporary directory for PyInstaller, Dill, Torch, SQLite
if getattr(sys, 'frozen', False):
    _base = Path(sys.executable).parent
else:
    _base = Path(__file__).resolve().parent.parent

_temp_dir = _base / "storage" / "temp"
try:
    _temp_dir.mkdir(parents=True, exist_ok=True)
    _temp_str = str(_temp_dir.resolve())
    os.environ["TMP"] = _temp_str
    os.environ["TEMP"] = _temp_str
    os.environ["TMPDIR"] = _temp_str
    tempfile.tempdir = _temp_str
except Exception:
    pass
