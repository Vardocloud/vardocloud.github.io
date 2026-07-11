#!/usr/bin/env python3
"""
Heartbeat Log — Supervisor Pattern için task durum takibi.

SQLite tabanlı, bağımlılıksız (stdlib only).
Supervisor'ın kendi akışına MÜDAHALE ETMEZ, sadece log tutar.

Kullanım:
    from heartbeat import HeartbeatLog
    hb = HeartbeatLog()
    hb.record("task-001", "running")
    hb.record("task-001", "completed", latency=12.4)
    hb.query("task-001")
    hb.summary()
"""

import sqlite3
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.environ.get(
    "HERMES_HEARTBEAT_DB",
    str(Path.home() / ".hermes" / "data" / "supervisor_heartbeat.db")
)


class HeartbeatLog:
    """
    Thread-safe olmayan basit heartbeat log.
    Supervisor pattern içinde her task spawn/complete/retry'de çağrılır.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS heartbeat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,         -- running|completed|failed|validation_failed|retrying|budget_exceeded
                schema_name TEXT,
                started_at REAL,              -- unix timestamp
                completed_at REAL,
                latency_seconds REAL,
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                metadata TEXT,                -- JSON blob
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_heartbeat_task_id 
            ON heartbeat(task_id)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_heartbeat_status 
            ON heartbeat(status)
        """)
        self._conn.commit()

    def record(self, task_id, status, schema_name=None, latency=None,
               retry_count=None, error_message=None, metadata=None):
        """
        Tek heartbeat kaydı.
        
        Parametreler:
            task_id: Benzersiz task tanımlayıcı (örn: "skool-scan-20260704")
            status:  running|completed|failed|validation_failed|retrying|budget_exceeded
            schema_name: Supervisor schema adı (opsiyonel)
            latency: Task tamamlanma süresi (saniye)
            retry_count: Kaçıncı deneme
            error_message: Hata mesajı
            metadata: Ek JSON veri (task_goal, provider, model vb.)
        """
        now = time.time()
        completed_at = now if status in ("completed", "failed", "validation_failed", "budget_exceeded") else None
        
        self._conn.execute("""
            INSERT INTO heartbeat 
                (task_id, status, schema_name, started_at, completed_at, 
                 latency_seconds, retry_count, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, status, schema_name, now, completed_at,
            latency, retry_count, error_message,
            json.dumps(metadata) if metadata else None
        ))
        self._conn.commit()

    def query(self, task_id, limit=10):
        """Belirli bir task'ın tüm heartbeat kayıtlarını döndürür."""
        cursor = self._conn.execute("""
            SELECT * FROM heartbeat 
            WHERE task_id = ? 
            ORDER BY id DESC 
            LIMIT ?
        """, (task_id, limit))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def recent(self, status=None, limit=10):
        """Son N heartbeat kaydı, opsiyonel status filtresiyle."""
        if status:
            cursor = self._conn.execute("""
                SELECT * FROM heartbeat 
                WHERE status = ? 
                ORDER BY id DESC 
                LIMIT ?
            """, (status, limit))
        else:
            cursor = self._conn.execute("""
                SELECT * FROM heartbeat 
                ORDER BY id DESC 
                LIMIT ?
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def summary(self, limit=5):
        """
        Son task'ların özet raporu.
        Her task_id için en son durumu + latency ortalamasını gösterir.
        """
        cursor = self._conn.execute("""
            SELECT 
                task_id,
                status,
                COUNT(*) as attempts,
                ROUND(AVG(latency_seconds), 1) as avg_latency,
                MAX(error_message) as last_error,
                datetime(MAX(created_at)) as last_seen
            FROM heartbeat
            GROUP BY task_id
            ORDER BY MAX(id) DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def failure_analysis(self, limit=10):
        """
        Başarısız task'ların analizi — validation_failed + hata mesajları.
        Supervisor'ın hangi pattern'lerde takıldığını görmek için.
        """
        cursor = self._conn.execute("""
            SELECT * FROM heartbeat 
            WHERE status IN ('failed', 'validation_failed', 'budget_exceeded')
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def cleanup(self, days=30):
        """30 günden eski logları temizler."""
        self._conn.execute("""
            DELETE FROM heartbeat 
            WHERE created_at < datetime('now', ?)
        """, (f"-{days} days",))
        self._conn.commit()
        return self._conn.total_changes

    def close(self):
        self._conn.close()


# --- CLI ---
if __name__ == "__main__":
    import sys
    
    hb = HeartbeatLog()
    
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  heartbeat.py record <task_id> <status> [--latency N] [--error MSG]")
        print("  heartbeat.py query <task_id>")
        print("  heartbeat.py recent [--status X] [--limit N]")
        print("  heartbeat.py summary [--limit N]")
        print("  heartbeat.py failures [--limit N]")
        print("  heartbeat.py cleanup [--days 30]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "record" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        status = sys.argv[3]
        latency = None
        error_msg = None
        if "--latency" in sys.argv:
            idx = sys.argv.index("--latency")
            latency = float(sys.argv[idx + 1])
        if "--error" in sys.argv:
            idx = sys.argv.index("--error")
            error_msg = sys.argv[idx + 1]
        hb.record(task_id, status, latency=latency, error_message=error_msg)
        print(f"✅ {task_id} → {status}")
    
    elif cmd == "query" and len(sys.argv) >= 3:
        rows = hb.query(sys.argv[2])
        for r in rows:
            print(f"  [{r['id']}] {r['task_id']} | {r['status']} | {r.get('latency_seconds','')}s | {r.get('error_message','')}")
    
    elif cmd == "recent":
        status = None
        limit = 10
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            status = sys.argv[idx + 1]
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        rows = hb.recent(status=status, limit=limit)
        for r in rows:
            print(f"  [{r['id']}] {r['task_id']} | {r['status']} | {r.get('latency_seconds','')}s")
    
    elif cmd == "summary":
        limit = 5
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        print("=== Son Task Özeti ===")
        for r in hb.summary(limit=limit):
            print(f"  {r['task_id']} → {r['status']} ({r['attempts']} deneme, avg {r.get('avg_latency','?')}s)")
            if r['last_error']:
                print(f"    ⚠️ {r['last_error']}")
    
    elif cmd == "failures":
        limit = 10
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        print("=== Başarısız Task'lar ===")
        for r in hb.failure_analysis(limit=limit):
            print(f"  [{r['id']}] {r['task_id']} → {r['status']} | {r.get('error_message','')}")
    
    elif cmd == "cleanup":
        days = 30
        if "--days" in sys.argv:
            idx = sys.argv.index("--days")
            days = int(sys.argv[idx + 1])
        deleted = hb.cleanup(days=days)
        print(f"🧹 {deleted} kayıt temizlendi ({days} gün +)")
    
    else:
        print(f"Bilinmeyen komut: {cmd}")
        sys.exit(1)
