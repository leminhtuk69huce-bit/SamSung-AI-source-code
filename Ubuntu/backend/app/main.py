import os
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ["PYTHONIOENCODING"] = "utf-8"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    STORAGE_DIR,
    BASE_DIR,
    BUNDLE_DIR
)
from .database import init_db
from .services.ocr_engine import get_ocr_engine
from .api.ocr_routes import router as ocr_router
from .api.history_routes import router as history_router
from .api.stats_routes import router as stats_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB initialized and preload OCR model
    print("=" * 60)
    print("[INFO] DANG KHOI DONG HE THONG BACKEND OCR CCCD/CMND...")
    print("=" * 60)
    try:
        init_db()
    except Exception as e:
        print(f"[WARN] Chu y khoi tao Database: {e}")
    # Preload OCR engine so first request is snappy
    try:
        get_ocr_engine()
    except Exception as e:
        print(f"[WARN] Chu y khoi tao OCR Engine: {e}")
    print("[OK] HE THONG BACKEND DA SAN SANG PHUC VU!")
    print("[INFO] Tai lieu API Swagger tai: http://localhost:8000/docs")
    print("=" * 60)
    yield
    # Shutdown
    print("[INFO] Dang tat he thong OCR Backend...")

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for seamless integration with any Frontend (React / Vite / Next / Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for saved images so frontend can render them
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# Mount demo UI
DEMO_DIR = None
for candidate in [
    BUNDLE_DIR / "demo_ui",
    BASE_DIR / "demo_ui",
    BASE_DIR.parent / "demo_ui",
    BUNDLE_DIR / "_internal" / "demo_ui",
]:
    if candidate.exists() and (candidate / "index.html").exists():
        DEMO_DIR = candidate
        break

if DEMO_DIR:
    app.mount("/demo", StaticFiles(directory=str(DEMO_DIR), html=True), name="demo")

# Include API routers
app.include_router(ocr_router)
app.include_router(history_router)
app.include_router(stats_router)

@app.get("/", summary="Root index")
async def root():
    from fastapi.responses import RedirectResponse
    # Redirect directly to demo UI if available
    if DEMO_DIR:
        return RedirectResponse(url="/demo")
    return JSONResponse({
        "app": API_TITLE,
        "version": API_VERSION,
        "status": "online",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    })

# ── Resilient Uvicorn Runner: auto-selects free port (8000 -> 8001 -> 8080) & keeps console open ──
try:
    import uvicorn
    import socket
    import webbrowser
    import threading
    import time

    def find_free_port(host: str, preferred_port: int = 8000) -> int:
        for p in [preferred_port, 8001, 8002, 8080, 8088]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, p))
                    return p
            except OSError:
                continue
        return preferred_port

    _original_uvicorn_run = uvicorn.run

    def resilient_uvicorn_run(fastapi_app, **kwargs):
        host = kwargs.get("host", "127.0.0.1")
        req_port = kwargs.get("port", 8000)
        actual_port = find_free_port(host, req_port)
        kwargs["port"] = actual_port
        url = f"http://{host}:{actual_port}/demo/"

        def open_browser():
            for _ in range(40):
                time.sleep(0.5)
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        if s.connect_ex((host, actual_port)) == 0:
                            time.sleep(0.3)
                            webbrowser.open(url)
                            return
                except Exception:
                    pass

        threading.Thread(target=open_browser, daemon=True).start()

        print("=" * 60)
        print(f"[INFO] AI OCR SERVER DANG CHAY TAI: {url}")
        print("   Nhan Ctrl+C de dung server.")
        print("=" * 60)

        try:
            _original_uvicorn_run(fastapi_app, **kwargs)
        except Exception as e:
            print(f"\n[LỖI SERVER]: {e}")
        finally:
            if sys.stdin and sys.stdin.isatty():
                print("\n[HỆ THỐNG ĐÃ TẮT] Nhấn Enter để đóng...")
                try:
                    input()
                except Exception:
                    pass

    uvicorn.run = resilient_uvicorn_run
except Exception as e:
    pass

