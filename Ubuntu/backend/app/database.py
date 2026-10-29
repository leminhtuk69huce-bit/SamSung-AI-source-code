import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import contextmanager
from .config import BASE_DIR


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
            test_conn = sqlite3.connect(str(candidate), timeout=5.0)
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
    """Context manager that guarantees connection is opened with WAL mode and ALWAYS closed cleanly."""
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    conn = sqlite3.connect(str(DB_FILE), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 10000;")
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
    """Initializes tables if they do not exist."""
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
                notes TEXT
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
        conn.commit()
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
                    is_verified, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                data.get("notes")
            ))
            conn.commit()
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
    """Updates fields of an existing record."""
    allowed_fields = [
        "id_number", "full_name", "date_of_birth", "gender", "nationality",
        "place_of_origin", "place_of_residence", "date_of_expiry",
        "date_of_issue", "issuing_authority", "identifying_features",
        "document_type", "is_verified", "notes"
    ]
    set_clauses = []
    params = []
    for k, v in updates.items():
        if k in allowed_fields:
            set_clauses.append(f"{k} = ?")
            params.append(v)

    if not set_clauses:
        return False

    params.append(record_id)
    with get_db() as conn:
        cur = conn.execute(
            f"UPDATE ocr_records SET {', '.join(set_clauses)} WHERE id = ?",
            params
        )
        conn.commit()
        return cur.rowcount > 0

def delete_record(record_id: str) -> bool:
    """Deletes a record by ID."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM ocr_records WHERE id = ?", (record_id,))
        conn.commit()
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

        # Type distribution
        type_rows = conn.execute("""
            SELECT document_type, COUNT(*) as count 
            FROM ocr_records 
            GROUP BY document_type
        """).fetchall()
        types = {r["document_type"]: r["count"] for r in type_rows}

        # Daily trend (last 7 days)
        trend_rows = conn.execute("""
            SELECT substr(created_at, 1, 10) as scan_date, COUNT(*) as count
            FROM ocr_records
            GROUP BY scan_date
            ORDER BY scan_date DESC
            LIMIT 7
        """).fetchall()
        trends = [{"date": r["scan_date"], "count": r["count"]} for r in reversed(trend_rows)]

        return {
            "total_scans": total_scans,
            "today_scans": today_scans,
            "average_confidence": round(float(avg_conf), 3),
            "average_processing_time_sec": round(float(avg_time), 2),
            "distribution_by_type": types,
            "recent_daily_trends": trends
        }
