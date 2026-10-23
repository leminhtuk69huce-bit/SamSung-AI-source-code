"""
card_detector.py — Module phát hiện và crop khung thẻ CCCD/CMND từ ảnh gốc.

Sử dụng OpenCV thuần túy (không cần model AI mới, không cần GPU).
Tốc độ: <0.05 giây mỗi ảnh trên CPU.

Pipeline:
  1. preprocess_for_detection()  — grayscale + GaussianBlur
  2. detect_edges()              — Canny với ngưỡng Otsu tự động
  3. find_card_contour()         — findContours + approxPolyDP 4 đỉnh
  4. perspective_warp()          — getPerspectiveTransform + warpPerspective
  5. detect_and_crop_card()      — hàm tổng hợp, fallback an toàn nếu thất bại
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def preprocess_for_detection(image: np.ndarray) -> np.ndarray:
    """
    Chuẩn bị ảnh cho bước phát hiện cạnh.
    Dùng GaussianBlur để loại bỏ nhiễu hạt nhỏ nhưng giữ cạnh thẻ.
    Không dùng threshold ngưỡng cứng vì ánh sáng webcam thay đổi liên tục.

    Args:
        image: ảnh BGR từ OpenCV (np.ndarray HxWx3)
    Returns:
        blurred: ảnh grayscale đã làm mờ (np.ndarray HxW)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred


def detect_edges(blurred: np.ndarray) -> np.ndarray:
    """
    Canny Edge Detection với ngưỡng tự động theo Otsu.
    Tránh hardcode ngưỡng vì điều kiện ánh sáng webcam thay đổi.

    Sau Canny, giãn nở (dilate) 2 lần để nối các đứt đoạn nhỏ ở cạnh thẻ.

    Args:
        blurred: ảnh grayscale đã blur (np.ndarray HxW)
    Returns:
        edges: ảnh nhị phân các cạnh (np.ndarray HxW)
    """
    # Tính ngưỡng Otsu tự động
    otsu_threshold, _ = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    lower = otsu_threshold * 0.5
    upper = otsu_threshold
    edges = cv2.Canny(blurred, lower, upper)

    # Giãn nở cạnh để nối các đứt đoạn
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=2)
    return edges


def find_card_contour(edges: np.ndarray, image_shape: tuple) -> Optional[np.ndarray]:
    """
    Tìm contour lớn nhất có dạng tứ giác (4 đỉnh) — đó là khung thẻ CCCD.

    Chiến lược:
    1. Tìm tất cả contour ngoài cùng (RETR_EXTERNAL)
    2. Sắp xếp theo diện tích giảm dần, chỉ xét 10 contour lớn nhất
    3. Thử xấp xỉ đa giác (approxPolyDP) với epsilon tăng dần (0.02 → 0.06)
    4. Chọn contour đầu tiên có đúng 4 đỉnh + diện tích 10%–98% diện tích ảnh

    Args:
        edges: ảnh nhị phân cạnh (np.ndarray HxW)
        image_shape: (h, w, ...) từ image.shape
    Returns:
        Array float32 4x2 tọa độ 4 góc thẻ, hoặc None nếu không tìm thấy.
    """
    h, w = image_shape[:2]
    image_area = float(h * w)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None

    # Sắp xếp theo diện tích giảm dần, chỉ lấy top 10
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        area = cv2.contourArea(contour)
        # Bỏ qua contour quá nhỏ (<10% ảnh) hoặc quá lớn (>98% ảnh — toàn khung)
        if area < image_area * 0.10 or area > image_area * 0.98:
            continue

        peri = cv2.arcLength(contour, True)
        if peri <= 0:
            continue

        # Thử nhiều epsilon để tìm xấp xỉ 4 đỉnh
        for eps_factor in [0.02, 0.03, 0.04, 0.05, 0.06]:
            approx = cv2.approxPolyDP(contour, eps_factor * peri, True)
            if len(approx) == 4:
                return approx.reshape(4, 2).astype(np.float32)

    return None  # Không tìm thấy khung thẻ → fallback toàn bộ ảnh


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Sắp xếp 4 điểm góc theo thứ tự chuẩn:
      [0] top-left, [1] top-right, [2] bottom-right, [3] bottom-left

    Kỹ thuật:
    - top-left:     tổng (x+y) nhỏ nhất
    - bottom-right: tổng (x+y) lớn nhất
    - top-right:    hiệu (x-y) nhỏ nhất  (x lớn, y nhỏ)
    - bottom-left:  hiệu (x-y) lớn nhất  (x nhỏ, y lớn)

    Args:
        pts: array float32 shape (4, 2)
    Returns:
        rect: array float32 shape (4, 2) đã sắp xếp
    """
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect


def perspective_warp(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    """
    Hiệu chỉnh phối cảnh (Perspective Transform):
    Biến đổi ảnh thẻ từ góc chụp nghiêng/lệch thành ảnh nhìn thẳng từ trên xuống.

    Kích thước đầu ra được tính động theo khoảng cách thực tế giữa các góc,
    đảm bảo thẻ luôn ở chiều ngang (width > height) theo tỷ lệ CCCD chuẩn 85.6×54mm.

    Args:
        image: ảnh BGR gốc (np.ndarray HxWx3)
        corners: array float32 4x2 — 4 góc thẻ theo thứ tự bất kỳ
    Returns:
        warped: ảnh BGR đã warp phẳng (np.ndarray H'xW'x3)
    """
    rect = order_points(corners)
    tl, tr, br, bl = rect

    # Chiều rộng đầu ra = max(khoảng cách cạnh trên, cạnh dưới)
    w_top = float(np.linalg.norm(tr - tl))
    w_bot = float(np.linalg.norm(br - bl))
    max_w = max(int(max(w_top, w_bot)), 1)

    # Chiều cao đầu ra = max(khoảng cách cạnh trái, cạnh phải)
    h_left = float(np.linalg.norm(bl - tl))
    h_right = float(np.linalg.norm(br - tr))
    max_h = max(int(max(h_left, h_right)), 1)

    # Đảm bảo thẻ nằm ngang (width > height) theo chuẩn CCCD
    if max_w < max_h:
        max_w, max_h = max_h, max_w

    # Điểm đích: hình chữ nhật phẳng chuẩn
    dst = np.array([
        [0,          0        ],
        [max_w - 1,  0        ],
        [max_w - 1,  max_h - 1],
        [0,          max_h - 1]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_w, max_h))
    return warped


def detect_and_crop_card(image: np.ndarray) -> Tuple[np.ndarray, bool]:
    """
    Hàm tổng hợp: Phát hiện và crop vùng thẻ CCCD/CMND từ ảnh gốc.

    Fallback an toàn: nếu bất kỳ bước nào thất bại (không tìm thấy thẻ,
    exception, crop quá nhỏ...), trả về ảnh gốc với cờ False —
    pipeline OCR phía sau vẫn chạy bình thường, không crash.

    Args:
        image: ảnh BGR OpenCV (np.ndarray HxWx3)
    Returns:
        (result_image, success_flag)
        - result_image: ảnh đã crop + warp nếu thành công, ảnh gốc nếu thất bại
        - success_flag: True nếu crop thành công, False nếu fallback
    """
    if image is None or image.size == 0:
        return image, False

    try:
        blurred = preprocess_for_detection(image)
        edges = detect_edges(blurred)
        corners = find_card_contour(edges, image.shape)

        if corners is not None:
            cropped = perspective_warp(image, corners)
            ch, cw = cropped.shape[:2]
            # Sanity check: ảnh crop phải đủ lớn để OCR có nghĩa
            if ch >= 60 and cw >= 100:
                return cropped, True

    except Exception as exc:
        try:
            print(f"[CARD_DETECT] Canh bao: khong the crop the CCCD: {exc}")
        except Exception:
            pass

    # Fallback: trả về ảnh gốc
    return image, False
