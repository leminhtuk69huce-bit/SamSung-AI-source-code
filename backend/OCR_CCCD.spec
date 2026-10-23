# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Fix Python 3.14 on Windows: run hooks in-process to avoid pipe crash
sys._pyi_isolated_subprocess = True

# Force UTF-8 and OpenMP compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_DIR = Path(r"E:\Samsung source code\backend")
WORKSPACE_DIR = BASE_DIR.parent

datas = [
    (str(WORKSPACE_DIR / "demo_ui"), "demo_ui"),
    (str(BASE_DIR / "models"), "models"),
]

hiddenimports = [
    # Uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    
    # FastAPI & Starlette
    "fastapi",
    "fastapi.staticfiles",
    "fastapi.middleware.cors",
    "starlette",
    "starlette.staticfiles",
    "multipart",
    "python_multipart",
    
    # App modules
    "app",
    "app.main",
    "app.config",
    "app.database",
    "app.schemas",
    "app.api.ocr_routes",
    "app.api.history_routes",
    "app.api.stats_routes",
    "app.services.ocr_engine",
    "app.services.preprocessor",
    "app.services.extractor",
    "app.services.export_service",

    # EasyOCR & Torch
    "easyocr",
    "torch",
    "torchvision",
    "cv2",
    "PIL",
    "openpyxl",
    "pandas",
    "sqlite3",
    "unittest",
]

a = Analysis(
    ["launcher.py"],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=["custom_hooks"],
    hooksconfig={},
    runtime_hooks=["hook_frozen_paths.py"],
    excludes=[
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "tkinter",
        "_tkinter",
        "matplotlib",
        "scipy.fft",
        "IPython",
        "notebook",
        "jupyter",
        "sqlalchemy",
        "dask",
        "bokeh",
        "docutils",
        "sphinx",
        "pyarrow",
        "botocore",
        "argon2",
        "nbformat",
        "pytest",
        "h5py",
        "lz4",
        "tensorflow",
        "onnxruntime",
        "tables",
        "distributed",
        "fsspec",
        "qtpy",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OCR_CCCD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="OCR_CCCD",
)
