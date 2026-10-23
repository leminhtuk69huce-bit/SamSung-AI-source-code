import cv2
import numpy as np
import base64
import io
import re
from PIL import Image
from typing import Tuple, Optional
from pathlib import Path

def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Reads raw image bytes into a BGR OpenCV NumPy array."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Không thể giải mã dữ liệu hình ảnh (ảnh hỏng hoặc không đúng định dạng).")
    return image

def read_image_from_path(filepath: str | Path) -> np.ndarray:
    """
    Safely reads an image from a filesystem path, fully supporting Unicode/Vietnamese filenames.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file ảnh: {filepath}")
    with open(path, "rb") as f:
        return read_image_from_bytes(f.read())

def read_image_from_base64(base64_str: str) -> np.ndarray:
    """
    Decodes base64 string (handles data URL prefixes like 'data:image/jpeg;base64,...').
    """
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    
    # Strip whitespace/newlines
    base64_str = re.sub(r"\s+", "", base64_str)
    try:
        decoded = base64.b64decode(base64_str)
        return read_image_from_bytes(decoded)
    except Exception as e:
        raise ValueError(f"Lỗi giải mã base64: {str(e)}")

def resize_for_ocr(image: np.ndarray, target_width: int = 1280) -> Tuple[np.ndarray, float]:
    """
    Resizes image while preserving aspect ratio to optimize OCR speed and accuracy.
    Returns (resized_image, scale_factor).
    """
    h, w = image.shape[:2]
    if w <= target_width and h <= target_width:
        return image, 1.0
    
    scale = target_width / float(w)
    new_w = target_width
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale

def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Applies gentle contrast enhancement (CLAHE on L-channel in LAB space)
    to boost text legibility on low-contrast cards.
    """
    try:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    except Exception:
        return image

def save_image_to_storage(image: np.ndarray, destination_path: Path) -> Optional[str]:
    """
    Saves an OpenCV BGR image safely to disk with Unicode path support.
    Resilient: catches any permission or disk errors and tries fallbacks,
    never throws an unhandled exception that disrupts the OCR pipeline.
    """
    try:
        destination_path = Path(destination_path)
        ext = destination_path.suffix.lower() or ".jpg"
        destination_path = destination_path.with_suffix(ext)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        success, encoded_img = cv2.imencode(ext, image)
        if not success:
            return None
            
        with open(destination_path, "wb") as f:
            f.write(encoded_img.tobytes())
        return str(destination_path)
    except Exception as e:
        print(f"⚠️ [STORAGE] Lưu ý: Không thể lưu ảnh vào {destination_path}: {e}")
        try:
            import tempfile
            import os
            fallback_dir = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "OCR_CCCD" / "storage"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            fallback_path = fallback_dir / destination_path.name
            with open(fallback_path, "wb") as f:
                f.write(encoded_img.tobytes())
            return str(fallback_path)
        except Exception:
            return None

