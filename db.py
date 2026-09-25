"""
SIF SENTINEL - SQLite Persistence Layer
Handles database schema, demo vs live data separation,
duplicate prevention, live KPI calculations, and HSE review status workflows.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sif_sentinel.db")

# Review Status Constants supporting both industry workflows
STATUS_PENDING = "Pending Review"
STATUS_CONFIRMED = "Reviewed"
STATUS_REJECTED = "Dismissed"
STATUS_NEEDS_REVIEW = "Escalated"

ALL_REVIEW_STATUSES = [
    "Reviewed",
    "Escalated",
    "Dismissed",
    "Pending Review",
    "CONFIRMED BY HSE",
    "PENDING HSE REVIEW",
    "REJECTED BY HSE",
    "NEEDS FURTHER REVIEW",
]

# Actionable statuses presented to HSE Officers
HSE_ACTION_STATUSES = [
    "Reviewed",
    "Escalated",
    "Dismissed",
    "Pending Review",
]


def get_db_connection():
    """Create a thread-safe connection with dict-like row access."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reseed: bool = False):
    """Initialize SQLite database schema and seed if empty or forced."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS reports")
        
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT UNIQUE NOT NULL,
        data_source TEXT NOT NULL DEFAULT 'DEMO',
        date TEXT NOT NULL,
        site TEXT NOT NULL,
        report_type TEXT NOT NULL,
        narrative TEXT NOT NULL,
        activity TEXT NOT NULL,
        sif_level TEXT NOT NULL,
        priority_score INTEGER NOT NULL,
        life_saving_rule TEXT NOT NULL,
        hazard TEXT NOT NULL,
        barrier TEXT NOT NULL,
        barrier_failure TEXT NOT NULL,
        potential_consequence TEXT NOT NULL,
        explanation TEXT NOT NULL,
        evidence TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        review_status TEXT NOT NULL,
        reviewer_name TEXT DEFAULT '',
        reviewer_comment TEXT DEFAULT '',
        review_date TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM reports")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        from seed_data import seed_database
        seed_database()


def get_kpis(source_filter: str = "ALL") -> Dict[str, Any]:
    """
    Calculate live KPIs directly from SQLite database on every call.
    Never cached stale; reflects immediately on new INSERT or UPDATE.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause = ""
    params = []
    if source_filter == "DEMO":
        where_clause = " WHERE data_source = 'DEMO'"
    elif source_filter == "LIVE":
        where_clause = " WHERE data_source = 'LIVE'"
        
    # Global counts for Demo vs Live separation banner
    cursor.execute("SELECT COUNT(*) FROM reports WHERE data_source = 'DEMO'")
    demo_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reports WHERE data_source = 'LIVE'")
    live_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reports")
    total_combined = cursor.fetchone()[0]
    
    # Filtered metrics based on source_filter
    cursor.execute(f"SELECT COUNT(*) FROM reports{where_clause}", params)
    total_in_view = cursor.fetchone()[0]
    
    prefix = f"{where_clause} AND" if where_clause else " WHERE"
    
    # SIF potential (High)
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} sif_level = 'HIGH'", params)
    sif_potential = cursor.fetchone()[0]
    
    # SIF Rate
    sif_rate = (sif_potential / total_in_view * 100.0) if total_in_view > 0 else 0.0
    
    # Pending HSE Review (High SIF)
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} review_status IN ('{STATUS_PENDING}', 'Pending Review', 'PENDING HSE REVIEW') AND sif_level = 'HIGH'", params)
    pending_review = cursor.fetchone()[0]
    
    # HSE Confirmed / Reviewed SIF
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} review_status IN ('{STATUS_CONFIRMED}', 'Reviewed', 'CONFIRMED BY HSE') AND sif_level = 'HIGH'", params)
    hse_confirmed = cursor.fetchone()[0]
    
    # HSE Rejected / Dismissed SIF
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} review_status IN ('{STATUS_REJECTED}', 'Dismissed', 'REJECTED BY HSE') AND sif_level = 'HIGH'", params)
    hse_rejected = cursor.fetchone()[0]
    
    # Needs Further Review / Escalated SIF
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} review_status IN ('{STATUS_NEEDS_REVIEW}', 'Escalated', 'NEEDS FURTHER REVIEW') AND sif_level = 'HIGH'", params)
    hse_needs_review = cursor.fetchone()[0]
    
    # Medium SIF reports
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} sif_level = 'MEDIUM'", params)
    medium_sif = cursor.fetchone()[0]
    
    # Low / Non-SIF reports
    cursor.execute(f"SELECT COUNT(*) FROM reports{prefix} sif_level IN ('LOW', 'NON-SIF', 'LOW / NON-SIF')", params)
    low_sif = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "demo_count": demo_count,
        "live_count": live_count,
        "total_combined": total_combined,
        "total_reports": total_in_view,
        "sif_potential": sif_potential,
        "sif_rate": round(sif_rate, 1),
        "pending_review": pending_review,
        "hse_confirmed": hse_confirmed,
        "hse_rejected": hse_rejected,
        "hse_needs_review": hse_needs_review,
        "medium_sif": medium_sif,
        "low_sif": low_sif,
    }


def save_report(report_data: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Save newly analyzed report to SQLite.
    Prevents duplicate insertion if the exact same narrative was already saved.
    Returns (report_id, is_duplicate).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    narrative_clean = report_data.get("narrative", "").strip()
    
    # Check for duplicate narrative
    cursor.execute("SELECT report_id FROM reports WHERE LOWER(narrative) = LOWER(?)", (narrative_clean,))
    existing = cursor.fetchone()
    if existing:
        existing_id = existing["report_id"]
        # Update existing record with any updated HSE disposition
        if "review_status" in report_data and report_data["review_status"]:
            cursor.execute("""
            UPDATE reports SET
                review_status = ?,
                reviewer_name = ?,
                reviewer_comment = ?,
                review_date = ?
            WHERE report_id = ?
            """, (
                report_data.get("review_status", STATUS_PENDING),
                report_data.get("reviewer_name", ""),
                report_data.get("reviewer_comment", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                existing_id
            ))
            conn.commit()
        conn.close()
        return existing_id, True

    # Generate unique Report ID
    now = datetime.now()
    cursor.execute("SELECT COALESCE(MAX(id), 0) FROM reports")
    max_id = cursor.fetchone()[0] + 1
    report_id = f"OIL-LIVE-{now.year}-{max_id:05d}"
    
    # Check ID collision safety
    cursor.execute("SELECT COUNT(*) FROM reports WHERE report_id = ?", (report_id,))
    if cursor.fetchone()[0] > 0:
        report_id = f"OIL-LIVE-{now.year}-{max_id:05d}-{now.strftime('%f')[:4]}"

    date_str = report_data.get("date", now.strftime("%Y-%m-%d %H:%M"))
    evidence_str = json.dumps(report_data.get("extracted_evidence", []))
    data_source = report_data.get("data_source", "LIVE")
    review_status = report_data.get("review_status", STATUS_PENDING)
    reviewer_name = report_data.get("reviewer_name", "")
    reviewer_comment = report_data.get("reviewer_comment", "")
    review_date = now.strftime("%Y-%m-%d %H:%M") if reviewer_name else ""
    
    cursor.execute("""
    INSERT INTO reports (
        report_id, data_source, date, site, report_type, narrative, activity,
        sif_level, priority_score, life_saving_rule, hazard,
        barrier, barrier_failure, potential_consequence, explanation,
        evidence, recommended_action, review_status, reviewer_name, reviewer_comment, review_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        data_source,
        date_str,
        report_data.get("site", "Duliajan Central Gas Plant"),
        report_data.get("report_type", "Near-Miss"),
        narrative_clean,
        report_data.get("activity", "Pipeline Maintenance"),
        report_data.get("sif_level", "HIGH"),
        int(report_data.get("priority_score", 85)),
        report_data.get("life_saving_rule", "Energy Isolation"),
        report_data.get("hazard", "Stored / Pressurized Energy"),
        report_data.get("barrier", "Energy Isolation & Zero-Energy Verification"),
        report_data.get("barrier_failure", "Zero-energy verification not completed"),
        report_data.get("potential_consequence", "High consequence"),
        report_data.get("explanation", ""),
        evidence_str,
        report_data.get("recommended_action", ""),
        review_status,
        reviewer_name,
        reviewer_comment,
        review_date
    ))
    
    conn.commit()
    conn.close()
    return report_id, False


def update_review_status(
    report_id: str,
    new_status: str,
    reviewer_name: str = "",
    reviewer_comment: str = ""
) -> bool:
    """Update review status live in SQLite with error handling."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute("""
    UPDATE reports SET
        review_status = ?,
        reviewer_name = CASE WHEN ? != '' THEN ? ELSE reviewer_name END,
        reviewer_comment = CASE WHEN ? != '' THEN ? ELSE reviewer_comment END,
        review_date = ?
    WHERE report_id = ?
    """, (new_status, reviewer_name, reviewer_name, reviewer_comment, reviewer_comment, now_str, report_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_all_reports(
    sif_level: Optional[str] = None,
    rule: Optional[str] = None,
    site: Optional[str] = None,
    activity: Optional[str] = None,
    data_source: Optional[str] = None,
    review_status: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 1500
) -> pd.DataFrame:
    """Query reports with full filtering."""
    conn = get_db_connection()
    query = "SELECT * FROM reports WHERE 1=1"
    params = []
    
    if data_source and data_source != "ALL":
        query += " AND data_source = ?"
        params.append(data_source)
        
    if sif_level and sif_level != "All":
        if sif_level == "LOW / NON-SIF":
            query += " AND sif_level IN ('LOW', 'NON-SIF', 'LOW / NON-SIF')"
        else:
            query += " AND sif_level = ?"
            params.append(sif_level)
            
    if rule and rule != "All":
        query += " AND life_saving_rule = ?"
        params.append(rule)
        
    if site and site != "All":
        query += " AND site = ?"
        params.append(site)

    if activity and activity != "All":
        query += " AND activity = ?"
        params.append(activity)
        
    if review_status and review_status != "All":
        if review_status in ("Reviewed", "CONFIRMED BY HSE"):
            query += " AND review_status IN ('Reviewed', 'CONFIRMED BY HSE')"
        elif review_status in ("Pending Review", "PENDING HSE REVIEW"):
            query += " AND review_status IN ('Pending Review', 'PENDING HSE REVIEW')"
        elif review_status in ("Dismissed", "REJECTED BY HSE"):
            query += " AND review_status IN ('Dismissed', 'REJECTED BY HSE')"
        elif review_status in ("Escalated", "NEEDS FURTHER REVIEW"):
            query += " AND review_status IN ('Escalated', 'NEEDS FURTHER REVIEW')"
        else:
            query += " AND review_status = ?"
            params.append(review_status)
        
    if search_query and search_query.strip():
        query += " AND (narrative LIKE ? OR report_id LIKE ? OR activity LIKE ? OR hazard LIKE ? OR reviewer_name LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term, term, term])
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full detail for a single report."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        try:
            data["evidence"] = json.loads(data["evidence"])
        except Exception:
            data["evidence"] = []
        return data
    return None
