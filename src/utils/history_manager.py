"""Classification history manager with SQLite persistent storage.

Stores every classification result locally so users can review past
predictions, track trends over time, and search/filter history.
"""

import os
import sqlite3
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default path for the history database.
# Use __file__ to resolve to the project root (src/utils → src → root)
# so the history dir is always colocated with the repo, regardless of CWD.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
HISTORY_DIR = os.path.join(_PROJECT_ROOT, "history")
DB_PATH = os.path.join(HISTORY_DIR, "classifications.db")


class HistoryManager:
    """Manages persistent classification history using SQLite.

    Stores email text, prediction, confidence, spam risk, model used,
    and optional metadata (URL analysis results, SHAP explanations).
    Provides stats aggregation and search/filter capabilities.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Create the database directory and table if they don't exist."""
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    email_text TEXT,
                    prediction TEXT NOT NULL,
                    confidence REAL,
                    spam_risk REAL,
                    model_used TEXT,
                    source TEXT DEFAULT 'manual',
                    url_count INTEGER DEFAULT 0,
                    suspicious_urls INTEGER DEFAULT 0,
                    metadata TEXT,
                    email_subject TEXT DEFAULT ''
                )
            """)
            # Create index for fast time-range queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON classifications(timestamp)
            """)
            conn.commit()
        finally:
            conn.close()

    def add_entry(
        self,
        email_text: str,
        prediction: str,
        confidence: Optional[float] = None,
        spam_risk: Optional[float] = None,
        model_used: Optional[str] = None,
        source: str = "manual",
        url_count: int = 0,
        suspicious_urls: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        email_subject: str = "",
    ) -> int:
        """Insert a new classification record.

        Args:
            email_text: The classified email text.
            prediction: 'Spam' or 'Ham'.
            confidence: Confidence percentage (0-100).
            spam_risk: Spam risk percentage (0-100).
            model_used: Name of the model used.
            source: Source of the classification ('manual', 'batch', 'api', 'live').
            url_count: Number of URLs found in the email.
            suspicious_urls: Number of suspicious URLs found.
            metadata: Optional dict with extra data (e.g., SHAP explanation summary).
            email_subject: Optional email subject line.

        Returns:
            The ID of the inserted record.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO classifications
                    (timestamp, email_text, prediction, confidence, spam_risk,
                     model_used, source, url_count, suspicious_urls, metadata, email_subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    email_text[:500] if email_text else "",
                    prediction,
                    confidence,
                    spam_risk,
                    model_used,
                    source,
                    url_count,
                    suspicious_urls,
                    json.dumps(metadata) if metadata else None,
                    email_subject,
                ),
            )
            conn.commit()
            record_id = cursor.lastrowid
            logger.debug(f"History entry #{record_id} saved: {prediction}")
            return record_id
        finally:
            conn.close()

    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
        prediction_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
        days_back: Optional[int] = None,
        search_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve classification history with filters.

        Args:
            limit: Maximum number of records to return.
            offset: Pagination offset.
            prediction_filter: Filter by prediction ('Spam' or 'Ham').
            source_filter: Filter by source ('manual', 'batch', 'api', 'live').
            days_back: Only return records from the last N days.
            search_text: Search keyword in email text or subject.

        Returns:
            List of classification record dicts, ordered by timestamp descending.
        """
        conditions = []
        params = []

        if prediction_filter:
            conditions.append("prediction = ?")
            params.append(prediction_filter)

        if source_filter:
            conditions.append("source = ?")
            params.append(source_filter)

        if days_back is not None:
            cutoff = time.time() - (days_back * 86400)
            conditions.append("timestamp >= ?")
            params.append(cutoff)

        if search_text:
            conditions.append("(email_text LIKE ? OR email_subject LIKE ?)")
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT id, timestamp, email_text, prediction, confidence, spam_risk,
                   model_used, source, url_count, suspicious_urls, metadata, email_subject
            FROM classifications
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                record = dict(row)
                record["timestamp"] = record["timestamp"]
                record["datetime"] = datetime.fromtimestamp(record["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if record["metadata"]:
                    try:
                        record["metadata"] = json.loads(record["metadata"])
                    except (json.JSONDecodeError, TypeError):
                        record["metadata"] = {}
                else:
                    record["metadata"] = {}
                results.append(record)
            return results
        finally:
            conn.close()

    def get_total_count(
        self,
        prediction_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
        days_back: Optional[int] = None,
        search_text: Optional[str] = None,
    ) -> int:
        """Get total record count matching filters (for pagination)."""
        conditions = []
        params = []

        if prediction_filter:
            conditions.append("prediction = ?")
            params.append(prediction_filter)

        if source_filter:
            conditions.append("source = ?")
            params.append(source_filter)

        if days_back is not None:
            cutoff = time.time() - (days_back * 86400)
            conditions.append("timestamp >= ?")
            params.append(cutoff)

        if search_text:
            conditions.append("(email_text LIKE ? OR email_subject LIKE ?)")
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM classifications WHERE {where_clause}", params
            ).fetchone()
            return row[0] if row else 0
        finally:
            conn.close()

    def get_stats(self, days_back: int = 30) -> Dict[str, Any]:
        """Compute aggregate statistics over the given period.

        Args:
            days_back: Number of days to analyze.

        Returns:
            Dict with stats: total, spam_count, ham_count, spam_pct,
            daily_counts (list of {date, spam, ham}), avg_confidence, etc.
        """
        cutoff = time.time() - (days_back * 86400)

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction = 'Spam' THEN 1 ELSE 0 END) as spam_count,
                    SUM(CASE WHEN prediction = 'Ham' THEN 1 ELSE 0 END) as ham_count,
                    AVG(confidence) as avg_confidence,
                    AVG(spam_risk) as avg_spam_risk,
                    SUM(url_count) as total_urls,
                    SUM(suspicious_urls) as total_suspicious_urls
                FROM classifications
                WHERE timestamp >= ?
                """,
                (cutoff,),
            ).fetchone()

            # Daily breakdown
            daily_rows = conn.execute(
                """
                SELECT
                    DATE(datetime(timestamp, 'unixepoch')) as day,
                    SUM(CASE WHEN prediction = 'Spam' THEN 1 ELSE 0 END) as spam,
                    SUM(CASE WHEN prediction = 'Ham' THEN 1 ELSE 0 END) as ham
                FROM classifications
                WHERE timestamp >= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (cutoff,),
            ).fetchall()

            daily_counts = [
                {"date": row[0], "spam": row[1] or 0, "ham": row[2] or 0}
                for row in daily_rows
            ]

            return {
                "total": cursor[0] or 0,
                "spam_count": cursor[1] or 0,
                "ham_count": cursor[2] or 0,
                "spam_pct": round((cursor[1] or 0) / max(cursor[0] or 1, 1) * 100, 1),
                "avg_confidence": round(cursor[3] or 0, 1),
                "avg_spam_risk": round(cursor[4] or 0, 1),
                "total_urls": cursor[5] or 0,
                "total_suspicious_urls": cursor[6] or 0,
                "daily_counts": daily_counts,
                "days_analyzed": days_back,
            }
        finally:
            conn.close()

    def clear_history(self, days_back: Optional[int] = None) -> int:
        """Delete classification records.

        Args:
            days_back: If set, only delete records older than N days.
                       If None, delete ALL records.

        Returns:
            Number of deleted records.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            if days_back is not None:
                cutoff = time.time() - (days_back * 86400)
                cursor = conn.execute(
                    "DELETE FROM classifications WHERE timestamp < ?",
                    (cutoff,),
                )
            else:
                cursor = conn.execute("DELETE FROM classifications")
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleared {deleted} history records")
            return deleted
        finally:
            conn.close()

    def get_entry_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single classification record by ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM classifications WHERE id = ?", (record_id,)
            ).fetchone()
            if row:
                record = dict(row)
                record["datetime"] = datetime.fromtimestamp(record["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if record["metadata"]:
                    try:
                        record["metadata"] = json.loads(record["metadata"])
                    except (json.JSONDecodeError, TypeError):
                        record["metadata"] = {}
                return record
            return None
        finally:
            conn.close()
