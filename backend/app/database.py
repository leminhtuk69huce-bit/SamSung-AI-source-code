import os
import sqlite3
import json
import uuid
import stat
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import contextmanager
from .config import BASE_DIR

FIELD_LABELS = {
    "id_number": "Số CCCD/CMND",
    "full_name": "Họ và tên",
    "date_of_birth": "Ngày sinh",
    "gender": "Giới tính",
    "nationality": "Quốc tịch",
    "place_of_origin": "Quê quán",
    "place_of_residence": "Nơi thường trú",
    "date_of_expiry": "Có giá trị đến",
    "date_of_issue": "Ngày cấp",
    "issuing_authority": "Nơi cấp",
    "identifying_features": "Đặc điểm nhận dạng",
    "notes": "Ghi chú"
}

def resolve_db_path() -> Path:
    """Finds or creates a writable path for the SQLite database."""
    candidates = [
        BASE_DIR / "ocr_database.db",
        Path.cwd() / "ocr_database.db",
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "OCR_CCCD" / "ocr_database.db"
    ]
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            if candidate.exists():
                try:
                    os.chmod(str(candidate), stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass
            test_conn = sqlite3.connect(str(candidate), timeout=5.0, isolation_level=None)
            test_conn.execute("PRAGMA journal_mode = WAL;")
            test_conn.execute("PRAGMA busy_timeout = 10000;")
            test_conn.execute("CREATE TABLE IF NOT EXISTS _test_rw (id INTEGER);")
            test_conn.close()
            return candidate
        except Exception:
            continue
    return BASE_DIR / "ocr_database.db"

DB_FILE = resolve_db_path()

@contextmanager
def get_db():
    """Context manager that guarantees connection is opened with autocommit & WAL mode, and ALWAYS closed cleanly."""
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DB_FILE.exists():
            try:
                os.chmod(str(DB_FILE), stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
    except Exception:
        pass

    conn = sqlite3.connect(
        str(DB_FILE),
        timeout=60.0,
        check_same_thread=False,
        isolation_level=None  # Autocommit mode: avoids implicit deferred lock accumulation
    )
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 30000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

def get_db_connection():
    """Compatibility wrapper returning get_db() context manager."""
    return get_db()

def init_db():
    """Initializes tables and migrates audit columns if they do not exist."""
    try:
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ocr_records (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    document_type TEXT NOT NULL DEFAULT 'CCCD_CHIP',
                    side TEXT NOT NULL DEFAULT 'FRONT',
                    id_number TEXT,
                    full_name TEXT,
                    date_of_birth TEXT,
                    gender TEXT,
                    nationality TEXT,
                    place_of_origin TEXT,
                    place_of_residence TEXT,
                    date_of_expiry TEXT,
                    date_of_issue TEXT,
                    issuing_authority TEXT,
                    identifying_features TEXT,
                    mrz_code TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    processing_time_sec REAL DEFAULT 0.0,
                    image_front_path TEXT,
                    image_back_path TEXT,
                    raw_detection_json TEXT,
                    is_verified INTEGER DEFAULT 0,
                    notes TEXT,
                    original_fields TEXT DEFAULT '',
                    edited_fields TEXT DEFAULT '',
                    edit_history TEXT DEFAULT ''
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ocr_records_created_at 
                ON ocr_records(created_at DESC);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ocr_records_id_number 
                ON ocr_records(id_number);
            """)
            
            # Check existing columns and migrate if necessary
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(ocr_records);")
            existing_cols = {row["name"] for row in cur.fetchall()}
            
            migration_columns = [
                ("original_fields", "TEXT DEFAULT ''"),
                ("edited_fields", "TEXT DEFAULT ''"),
                ("edit_history", "TEXT DEFAULT ''")
            ]
            for col_name, col_def in migration_columns:
                if col_name not in existing_cols:
                    try:
                        conn.execute(f"ALTER TABLE ocr_records ADD COLUMN {col_name} {col_def};")
                    except Exception:
                        pass
    except Exception as e:
        try:
            print(f"[DATABASE] Luu y khi tao bang SQLite: {e}")
        except Exception:
            pass

def json_default_serializer(obj):
    if hasattr(obj, "item"):
        return obj.item()
    if hasattr(obj, "tolist"):
        return obj.tolist()
    return str(obj)

def save_record(data: Dict[str, Any]) -> str:
    """Inserts a new OCR record and returns its ID."""
    record_id = data.get("id") or str(uuid.uuid4())
    created_at = data.get("created_at") or datetime.now().isoformat()
    
    raw_json = data.get("raw_detection_json")
    if isinstance(raw_json, (dict, list)):
        raw_json_str = json.dumps(raw_json, ensure_ascii=False, default=json_default_serializer)
    else:
        raw_json_str = str(raw_json) if raw_json else "{}"

    # Snapshot of initial extracted fields for audit & diff
    original_dict = {
        "id_number": data.get("id_number") or "",
        "full_name": data.get("full_name") or "",
        "date_of_birth": data.get("date_of_birth") or "",
        "gender": data.get("gender") or "",
        "nationality": data.get("nationality") or "Việt Nam",
        "place_of_origin": data.get("place_of_origin") or "",
        "place_of_residence": data.get("place_of_residence") or "",
        "date_of_expiry": data.get("date_of_expiry") or "",
        "date_of_issue": data.get("date_of_issue") or "",
        "issuing_authority": data.get("issuing_authority") or "",
        "identifying_features": data.get("identifying_features") or ""
    }
    original_fields_str = json.dumps(original_dict, ensure_ascii=False)

    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO ocr_records (
                    id, created_at, document_type, side,
                    id_number, full_name, date_of_birth, gender, nationality,
                    place_of_origin, place_of_residence, date_of_expiry,
                    date_of_issue, issuing_authority, identifying_features, mrz_code,
                    confidence_score, processing_time_sec,
                    image_front_path, image_back_path, raw_detection_json,
                    is_verified, notes, original_fields, edited_fields, edit_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                created_at,
                data.get("document_type", "CCCD_CHIP"),
                data.get("side", "FRONT"),
                data.get("id_number"),
                data.get("full_name"),
                data.get("date_of_birth"),
                data.get("gender"),
                data.get("nationality", "Việt Nam"),
                data.get("place_of_origin"),
                data.get("place_of_residence"),
                data.get("date_of_expiry"),
                data.get("date_of_issue"),
                data.get("issuing_authority"),
                data.get("identifying_features"),
                data.get("mrz_code"),
                float(data.get("confidence_score", 0.0)),
                float(data.get("processing_time_sec", 0.0)),
                data.get("image_front_path"),
                data.get("image_back_path"),
                raw_json_str,
                int(data.get("is_verified", 0)),
                data.get("notes") or "",
                original_fields_str,
                "",
                ""
            ))
    except Exception as e:
        try:
            print(f"[DB] Khong the luu ban ghi SQLite: {e}")
        except Exception:
            pass
    return record_id

def get_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single record by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM ocr_records WHERE id = ?", (record_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("raw_detection_json"):
            try:
                d["raw_detection_json"] = json.loads(d["raw_detection_json"])
            except Exception:
                pass
        return d

def list_records(
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    side: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Lists records with optional search and pagination."""
    query = "SELECT * FROM ocr_records WHERE 1=1"
    params: List[Any] = []

    if search:
        query += " AND (full_name LIKE ? OR id_number LIKE ? OR place_of_residence LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    
    if document_type:
        query += " AND document_type = ?"
        params.append(document_type)

    if side:
        query += " AND side = ?"
        params.append(side)

    # Count total
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    with get_db() as conn:
        total = conn.execute(count_query, params).fetchone()[0]

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()

        items = []
        for r in rows:
            d = dict(r)
            if d.get("raw_detection_json"):
                try:
                    d["raw_detection_json"] = json.loads(d["raw_detection_json"])
                except Exception:
                    pass
            items.append(d)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

def update_record(record_id: str, updates: Dict[str, Any]) -> bool:
    """Updates fields of an existing record and automatically tracks human modifications."""
    allowed_fields = [
        "id_number", "full_name", "date_of_birth", "gender", "nationality",
        "place_of_origin", "place_of_residence", "date_of_expiry",
        "date_of_issue", "issuing_authority", "identifying_features",
        "document_type", "is_verified", "notes"
    ]
    
    existing = get_record_by_id(record_id)
    if not existing:
        return False

    # Retrieve initial snapshot if exists, otherwise fallback to existing record
    orig_dict = {}
    if existing.get("original_fields"):
        try:
            orig_dict = json.loads(existing["original_fields"])
        except Exception:
            orig_dict = {}

    changed_labels = []
    change_details = []

    for field, label in FIELD_LABELS.items():
        if field in updates:
            new_val = str(updates[field] or "").strip()
            # Compare with original snapshot if available, else existing in db
            old_base_val = str(orig_dict.get(field, existing.get(field) or "")).strip()
            if new_val != old_base_val and (new_val or old_base_val):
                changed_labels.append(label)
                old_display = old_base_val if old_base_val else "Trống"
                new_display = new_val if new_val else "Xóa"
                change_details.append(f"{label}: [OCR gốc: '{old_display}'] ➔ [Người dùng sửa: '{new_display}']")

    set_clauses = []
    params = []
    for k, v in updates.items():
        if k in allowed_fields:
            set_clauses.append(f"{k} = ?")
            params.append(v)

    # Always mark as verified when confirmed
    if "is_verified" not in updates:
        set_clauses.append("is_verified = ?")
        params.append(1)

    if changed_labels:
        edited_str = ", ".join(changed_labels)
        history_str = "; ".join(change_details)
    else:
        edited_str = existing.get("edited_fields") or "Giữ nguyên kết quả quét gốc"
        history_str = existing.get("edit_history") or "Không chỉnh sửa"

    set_clauses.append("edited_fields = ?")
    params.append(edited_str)
    set_clauses.append("edit_history = ?")
    params.append(history_str)

    params.append(record_id)
    with get_db() as conn:
        cur = conn.execute(
            f"UPDATE ocr_records SET {', '.join(set_clauses)} WHERE id = ?",
            params
        )
        return cur.rowcount > 0

def delete_record(record_id: str) -> bool:
    """Deletes a record by ID."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM ocr_records WHERE id = ?", (record_id,))
        return cur.rowcount > 0

def get_statistics() -> Dict[str, Any]:
    """Computes high-level statistics for dashboard."""
    with get_db() as conn:
        total_scans = conn.execute("SELECT COUNT(*) FROM ocr_records").fetchone()[0]
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_scans = conn.execute(
            "SELECT COUNT(*) FROM ocr_records WHERE created_at LIKE ?", 
            (f"{today_date}%",)
        ).fetchone()[0]

        avg_conf = conn.execute(
            "SELECT AVG(confidence_score) FROM ocr_records WHERE confidence_score > 0"
        ).fetchone()[0] or 0.0

        avg_time = conn.execute(
            "SELECT AVG(processing_time_sec) FROM ocr_records WHERE processing_time_sec > 0"
        ).fetchone()[0] or 0.0

        type_rows = conn.execute(
            "SELECT document_type, COUNT(*) as cnt FROM ocr_records GROUP BY document_type"
        ).fetchall()
        types = {r["document_type"]: r["cnt"] for r in type_rows}

        trend_rows = conn.execute("""
            SELECT SUBSTR(created_at, 1, 10) as day, COUNT(*) as cnt 
            FROM ocr_records 
            GROUP BY day 
            ORDER BY day DESC 
            LIMIT 7
        """).fetchall()
        trends = [{"date": r["day"], "count": r["cnt"]} for r in reversed(trend_rows)]

        return {
            "total_scans": total_scans,
            "today_scans": today_scans,
            "average_confidence": round(avg_conf, 3),
            "average_processing_time_sec": round(avg_time, 2),
            "distribution_by_type": types,
            "recent_daily_trends": trends
        }
