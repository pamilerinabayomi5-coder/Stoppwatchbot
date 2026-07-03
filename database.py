import sqlite3
from datetime import datetime, timezone
from config import DATABASE_PATH, logger

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    join_date TEXT NOT NULL
                )
            """)
            
            # Stopwatch State Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stopwatch (
                    user_id INTEGER PRIMARY KEY,
                    start_timestamp TEXT,
                    pause_timestamp TEXT,
                    accumulated_seconds REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'STOPPED',
                    last_updated TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    start_time TEXT,
                    stop_time TEXT,
                    total_elapsed TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Rate Limiting Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    user_id INTEGER PRIMARY KEY,
                    last_request_time REAL
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)

def save_user(user_id: int, username: str, first_name: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, now)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error saving user {user_id}: {e}")

def get_stopwatch(user_id: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stopwatch WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Database error fetching stopwatch for {user_id}: {e}")
        return None

def save_stopwatch(user_id: int, start_ts: str, pause_ts: str, accumulated: float, status: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO stopwatch (user_id, start_timestamp, pause_timestamp, accumulated_seconds, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    start_timestamp=excluded.start_timestamp,
                    pause_timestamp=excluded.pause_timestamp,
                    accumulated_seconds=excluded.accumulated_seconds,
                    status=excluded.status,
                    last_updated=excluded.last_updated
            """, (user_id, start_ts, pause_ts, accumulated, status, now))
            conn.commit()
    except Exception as e:
        logger.error(f"Database error updating stopwatch for {user_id}: {e}")

def add_history_record(user_id: int, start_time: str, stop_time: str, total_elapsed: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (user_id, start_time, stop_time, total_elapsed) VALUES (?, ?, ?, ?)",
                (user_id, start_time, stop_time, total_elapsed)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database error inserting history for {user_id}: {e}")

def get_user_history(user_id: int, limit: int = 10):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT start_time, stop_time, total_elapsed FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database error pulling history for {user_id}: {e}")
        return []
