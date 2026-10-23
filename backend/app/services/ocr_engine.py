import sys
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ..config import OCR_LANGUAGES, OCR_GPU, BASE_DIR, BUNDLE_DIR
import easyocr
import threading
import numpy as np
from typing import List, Tuple, Dict, Any


class OCREngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(OCREngine, cls).__new__(cls)
                    cls._instance._initialize_reader()
        return cls._instance

    def _initialize_reader(self):
        print(f"[OCR] Đang khởi tạo EasyOCR Reader với ngôn ngữ {OCR_LANGUAGES}, GPU={OCR_GPU}...")
        
        # Check for offline bundled models directory
        model_storage = None
        for candidate in [
            BASE_DIR / "models",
            BUNDLE_DIR / "models",
            BUNDLE_DIR / "_internal" / "models",
        ]:
            if candidate.exists() and (candidate / "craft_mlt_25k.pth").exists():
                model_storage = str(candidate)
                break

        reader_kwargs = {
            "lang_list": OCR_LANGUAGES,
            "gpu": OCR_GPU,
            "detector": True,
            "recognizer": True
        }
        if model_storage:
            print(f"[OCR] Sử dụng mô hình AI ngoại tuyến từ: {model_storage}")
            reader_kwargs["model_storage_directory"] = model_storage
            reader_kwargs["download_enabled"] = False

        self.reader = easyocr.Reader(**reader_kwargs)
        print("[OCR] Khởi tạo EasyOCR Reader thành công!")

    def run_ocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs OCR on the given BGR image.
        Returns a list of dicts with:
          - 'box': [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
          - 'text': string recognized text
          - 'confidence': float between 0.0 and 1.0
          - 'center_y': average Y coordinate for line grouping
          - 'center_x': average X coordinate
        """
        with self._lock:
            # easyocr takes RGB or BGR or filepath
            results = self.reader.readtext(image)

        structured_results = []
        for item in results:
            box, text, conf = item
            box_points = [[float(pt[0]), float(pt[1])] for pt in box]
            xs = [float(pt[0]) for pt in box]
            ys = [float(pt[1]) for pt in box]
            center_x = float(sum(xs) / len(xs))
            center_y = float(sum(ys) / len(ys))

            cleaned_text = str(text).strip()
            if cleaned_text:
                structured_results.append({
                    "box": box_points,
                    "text": cleaned_text,
                    "confidence": round(float(conf), 4),
                    "center_x": round(center_x, 2),
                    "center_y": round(center_y, 2),
                    "min_x": round(float(min(xs)), 2),
                    "max_x": round(float(max(xs)), 2),
                    "min_y": round(float(min(ys)), 2),
                    "max_y": round(float(max(ys)), 2),
                })

        # Sort top-to-bottom, then left-to-right
        structured_results.sort(key=lambda r: (r["center_y"], r["center_x"]))
        return structured_results

# Global engine instance getter
def get_ocr_engine() -> OCREngine:
    return OCREngine()
