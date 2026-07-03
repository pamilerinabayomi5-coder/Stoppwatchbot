from datetime import datetime, timezone
import database
from utils import format_seconds

def calculate_current_elapsed(row) -> float:
    if not row:
        return 0.0
    
    accumulated = row['accumulated_seconds'] or 0.0
    status = row['status']
    
    if status == 'RUNNING' and row['start_timestamp']:
        start_dt = datetime.fromisoformat(row['start_timestamp'])
        now = datetime.now(timezone.utc)
        delta = (now - start_dt).total_seconds()
        return accumulated + delta
    
    return accumulated

def start_session(user_id: int) -> tuple[bool, str]:
    row = database.get_stopwatch(user_id)
    if row and row['status'] == 'RUNNING':
        return False, "⚠️ Your stopwatch is already running!"
        
    now_str = datetime.now(timezone.utc).isoformat()
    
    if row and row['status'] == 'PAUSED':
        # Treat as resume
        database.save_stopwatch(user_id, now_str, None, row['accumulated_seconds'], 'RUNNING')
    else:
        # Brand new or stopped reset state
        database.save_stopwatch(user_id, now_str, None, 0.0, 'RUNNING')
        
    return True, "▶️ Stopwatch started!"

def pause_session(user_id: int) -> tuple[bool, str]:
    row = database.get_stopwatch(user_id)
    if not row or row['status'] == 'STOPPED':
        return False, "⚠️ Cannot pause a stopwatch that hasn't started!"
    if row['status'] == 'PAUSED':
        return False, "⚠️ Stopwatch is already paused!"
        
    now = datetime.now(timezone.utc)
    start_dt = datetime.fromisoformat(row['start_timestamp'])
    delta = (now - start_dt).total_seconds()
    new_accumulated = (row['accumulated_seconds'] or 0.0) + delta
    
    database.save_stopwatch(user_id, None, now.isoformat(), new_accumulated, 'PAUSED')
    return True, f"⏸️ Stopwatch paused at *{format_seconds(new_accumulated)}*."

def resume_session(user_id: int) -> tuple[bool, str]:
    row = database.get_stopwatch(user_id)
    if not row or row['status'] == 'STOPPED':
        return False, "⚠️ Cannot resume a stopwatch that hasn't started!"
    if row['status'] == 'RUNNING':
        return False, "⚠️ Stopwatch is already running!"
        
    now_str = datetime.now(timezone.utc).isoformat()
    database.save_stopwatch(user_id, now_str, None, row['accumulated_seconds'], 'RUNNING')
    return True, "▶️ Stopwatch resumed!"

def stop_session(user_id: int) -> tuple[bool, str]:
    row = database.get_stopwatch(user_id)
    if not row or row['status'] == 'STOPPED':
        return False, "⚠️ The stopwatch is not active right now."
        
    total_seconds = calculate_current_elapsed(row)
    now_str = datetime.now(timezone.utc).isoformat()
    
    start_readable = row['start_timestamp'] if row['start_timestamp'] else row['last_updated']
    formatted_duration = format_seconds(total_seconds)
    
    # Commit state reset
    database.save_stopwatch(user_id, None, None, 0.0, 'STOPPED')
    
    # Log historic data 
    database.add_history_record(user_id, start_readable, now_str, formatted_duration)
    
    msg = (
        "⏹️ *Stopwatch Stopped!*\n\n"
        f"⏱️ *Total Time:* `{formatted_duration}`\n"
    )
    return True, msg

def reset_session(user_id: int) -> tuple[bool, str]:
    row = database.get_stopwatch(user_id)
    if not row or (row['status'] == 'STOPPED' and row['accumulated_seconds'] == 0.0):
        return False, "⚠️ The stopwatch is already clean and reset."
        
    database.save_stopwatch(user_id, None, None, 0.0, 'STOPPED')
    return True, "🔄 Stopwatch has been reset to `00:00:00`."
