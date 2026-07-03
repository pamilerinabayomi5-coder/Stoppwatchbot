import time
from datetime import datetime, timezone
import re
from database import get_db_connection

def format_seconds(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_iso_to_readable(iso_str: str) -> str:
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return iso_str

def escape_markdown(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def is_rate_limited(user_id: int, cooldown: float = 1.0) -> bool:
    """Returns True if the user is clicking or typing too fast."""
    now = time.time()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_request_time FROM rate_limits WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                last_time = row['last_request_time']
                if now - last_time < cooldown:
                    return True
                cursor.execute("UPDATE rate_limits SET last_request_time = ? WHERE user_id = ?", (now, user_id))
            else:
                cursor.execute("INSERT INTO rate_limits (user_id, last_request_time) VALUES (?, ?)", (user_id, now))
            conn.commit()
    except Exception:
        # Fail-open under database load issues to prevent blocking users entirely
        return False
    return False
