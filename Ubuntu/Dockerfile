FROM python:3.10-slim

# Cài đặt thư viện hệ thống cần thiết cho OpenCV và xử lý hình ảnh
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Sao chép mã nguồn và mô hình AI
COPY backend/ /app/backend/
COPY demo_ui/ /app/demo_ui/
COPY tests/ /app/tests/

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    KMP_DUPLICATE_LIB_OK=TRUE

# Port chạy ứng dụng
EXPOSE 8000

# Khởi chạy server
CMD ["python", "backend/run_backend.py"]
