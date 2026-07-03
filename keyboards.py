from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard(status: str = 'STOPPED') -> InlineKeyboardMarkup:
    keyboard = []
    
    if status == 'RUNNING':
        keyboard.append([
            InlineKeyboardButton("⏸ Pause", callback_data="btn_pause"),
            InlineKeyboardButton("⏹ Stop", callback_data="btn_stop")
        ])
    elif status == 'PAUSED':
        keyboard.append([
            InlineKeyboardButton("▶ Resume", callback_data="btn_resume"),
            InlineKeyboardButton("🔄 Reset", callback_data="btn_reset")
        ])
    else:  # STOPPED
        keyboard.append([
            InlineKeyboardButton("▶ Start", callback_data="btn_start")
        ])
        
    # Standard utility controls layout
    keyboard.append([
        InlineKeyboardButton("⏱ Status", callback_data="btn_status"),
        InlineKeyboardButton("📜 History", callback_data="btn_history")
    ])
    keyboard.append([
        InlineKeyboardButton("❓ Help", callback_data="btn_help"),
        InlineKeyboardButton("ℹ About", callback_data="btn_about")
    ])
    
    return InlineKeyboardMarkup(keyboard)
