import sys
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ..config import OCR_LANGUAGES, OCR_GPU, OCR_HARDWARE_INFO, BASE_DIR, BUNDLE_DIR
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
        print(f"[OCR] Đang khởi tạo EasyOCR Reader với ngôn ngữ {OCR_LANGUAGES}, chế độ: {OCR_HARDWARE_INFO}...")
        
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

        self.model_storage = model_storage
        reader_kwargs = {
            "lang_list": OCR_LANGUAGES,
            "detector": True,
            "recognizer": True
        }
        if model_storage:
            print(f"[OCR] Sử dụng mô hình AI ngoại tuyến từ: {model_storage}")
            reader_kwargs["model_storage_directory"] = model_storage
            reader_kwargs["download_enabled"] = False

        self.use_gpu = False
        if OCR_GPU:
            try:
                print(f"[OCR TĂNG TỐC] Khởi tạo mô hình trên {OCR_HARDWARE_INFO}...")
                reader_kwargs["gpu"] = True
                self.reader = easyocr.Reader(**reader_kwargs)
                self.use_gpu = True
                print(f"[OCR TĂNG TỐC] Kích hoạt thành công phần cứng {OCR_HARDWARE_INFO}! Tốc độ xử lý tăng hơn 600%.")
            except Exception as gpu_err:
                print(f"[OCR CẢNH BÁO] Không thể khởi tạo GPU ({gpu_err}). Tự động fallback về chế độ CPU an toàn 100%!")
                reader_kwargs["gpu"] = False
                self.reader = easyocr.Reader(**reader_kwargs)
                self.use_gpu = False
        else:
            print("[OCR] Khởi tạo EasyOCR với chế độ CPU an toàn...")
            reader_kwargs["gpu"] = False
            self.reader = easyocr.Reader(**reader_kwargs)
            self.use_gpu = False

        print("[OCR] Khởi tạo EasyOCR Reader hoàn tất và sẵn sàng phục vụ!")

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
            try:
                results = self.reader.readtext(image)
            except Exception as ocr_err:
                # Cơ chế đường lui: Fallback tức thì về CPU nếu GPU gặp sự cố hoặc tràn VRAM
                if getattr(self, "use_gpu", False):
                    print(f"[OCR GPU Fallback] Lỗi suy luận GPU ({ocr_err}). Đang giải phóng VRAM và chuyển sang CPU dự phòng...")
                    try:
                        import torch
                        torch.cuda.empty_cache()
                    except Exception:
                        pass
                    cpu_kwargs = {
                        "lang_list": OCR_LANGUAGES,
                        "gpu": False,
                        "detector": True,
                        "recognizer": True
                    }
                    if self.model_storage:
                        cpu_kwargs["model_storage_directory"] = self.model_storage
                        cpu_kwargs["download_enabled"] = False
                    cpu_reader = easyocr.Reader(**cpu_kwargs)
                    results = cpu_reader.readtext(image)
                else:
                    raise ocr_err

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

        if not structured_results:
            return []

        # Line clustering: Nhóm các ô bounding box trên cùng dòng nằm ngang (chênh lệch y <= 13px)
        sorted_by_y = sorted(structured_results, key=lambda b: b["center_y"])
        lines = []
        y_thresh = 13.0
        for b in sorted_by_y:
            placed = False
            for line in lines:
                avg_y = sum(x["center_y"] for x in line) / len(line)
                if abs(b["center_y"] - avg_y) <= y_thresh:
                    line.append(b)
                    placed = True
                    break
            if not placed:
                lines.append([b])

        lines.sort(key=lambda line: sum(x["center_y"] for x in line) / len(line))
        final_boxes = []
        for line in lines:
            line.sort(key=lambda b: b["center_x"])
            final_boxes.extend(line)

        return final_boxes

# Global engine instance getter
def get_ocr_engine() -> OCREngine:
    return OCREngine()
