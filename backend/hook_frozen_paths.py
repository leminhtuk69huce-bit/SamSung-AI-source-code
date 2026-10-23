"""
PyInstaller Runtime Hook — Fixes path resolution for EasyOCR, Torch, OpenCV
when running inside a frozen (EXE) environment.
Place this file as: backend/hook_frozen_paths.py
Then reference in OCR_CCCD.spec -> runtime_hooks=['hook_frozen_paths.py']
"""
import os
import sys

# Force UTF-8 on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Set KMP flag before any torch import happens
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    meipass = sys._MEIPASS
    
    # Let EasyOCR find its model data inside the bundle
    os.environ.setdefault("EASYOCR_MODULE_PATH", meipass)
    
    # Tell torch where its lib data is
    torch_lib = os.path.join(meipass, 'torch', 'lib')
    if os.path.exists(torch_lib):
        # Prepend torch lib to PATH so DLLs are found
        os.environ['PATH'] = torch_lib + os.pathsep + os.environ.get('PATH', '')
    
    # OpenCV data path
    cv2_data = os.path.join(meipass, 'cv2', 'data')
    if os.path.exists(cv2_data):
        os.environ.setdefault('OPENCV_DATA_PATH', cv2_data)
    
    # Add meipass to sys.path so app modules are importable
    if meipass not in sys.path:
        sys.path.insert(0, meipass)
    
    # Change working directory to the EXE's folder (not _MEIPASS temp dir)
    exe_dir = os.path.dirname(sys.executable)
    os.chdir(exe_dir)
