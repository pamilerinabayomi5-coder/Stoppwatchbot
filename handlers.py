from telegram import Update
from telegram.ext import ContextTypes
import database
import stopwatch
from keyboards import get_main_keyboard
from utils import format_seconds, escape_markdown, is_rate_limited, format_iso_to_readable

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.save_user(user.id, user.username, user.first_name)
    
    row = database.get_stopwatch(user.id)
    current_status = row['status'] if row else 'STOPPED'
    
    welcome_text = (
        f"👋 Welcome *{escape_markdown(user.first_name)}* to *StopwatchBot*!\n\n"
        "Your ultra-clean, cloud-persisted personal timing assistant. Use the layout below to navigate effortlessly."
    )
    await update.message.reply_text(
        text=welcome_text,
        parse_mode="MarkdownV2",
        reply_markup=get_main_keyboard(current_status)
    )

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    records = database.get_user_history(user.id, limit=10)
    
    if not records:
        await update.message.reply_text("📜 You have no historic timing records yet.")
        return
        
    msg = "📜 *Your Last 10 Sessions:*\n\n"
    for idx, r in enumerate(records, 1):
        # Prefixed string with 'fr' to eliminate Python 3.14 literal syntax warnings
        msg += fr"{idx}\. `{r['total_elapsed']}` \(Ended: {escape_markdown(format_iso_to_readable(r['stop_time']))}\)\n"
        
    await update.message.reply_text(text=msg, parse_mode="MarkdownV2")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ *How to use StopwatchBot:*\n\n"
        "▶ *Start*: Initialise active stopwatch record.\n"
        "⏸ *Pause*: Pause calculation without discarding time.\n"
        "▶ *Resume*: Continue timing execution instantly.\n"
        "⏹ *Stop*: Halt and commit runtime profile to History.\n"
        "🔄 *Reset*: Wipe out active counter values cleanly.\n\n"
        "💡 _State handles correctly across network dropouts or server updates seamlessly._"
    )
    await update.message.reply_text(text=help_text, parse_mode="MarkdownV2")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    if is_rate_limited(user_id):
        await query.answer("⚠️ Processing fast requests... please wait a moment.", show_alert=True)
        return

    await query.answer()
    
    row = database.get_stopwatch(user_id)
    current_status = row['status'] if row else 'STOPPED'
    
    response_text = ""
    
    if data == "btn_start":
        success, response_text = stopwatch.start_session(user_id)
    elif data == "btn_pause":
        success, response_text = stopwatch.pause_session(user_id)
    elif data == "btn_resume":
        success, response_text = stopwatch.resume_session(user_id)
    elif data == "btn_reset":
        success, response_text = stopwatch.reset_session(user_id)
    elif data == "btn_stop":
        success, response_text = stopwatch.stop_session(user_id)
    elif data == "btn_status":
        elapsed = stopwatch.calculate_current_elapsed(row)
        response_text = f"⏱️ *Current Status:* `{current_status}`\n⏳ *Elapsed:* `{format_seconds(elapsed)}`"
    elif data == "btn_history":
        records = database.get_user_history(user_id, limit=10)
        if not records:
            response_text = "📜 You have no historic timing records yet."
        else:
            response_text = "📜 *Your Last 10 Sessions:*\n\n"
            for idx, r in enumerate(records, 1):
                response_text += f"{idx}. `{r['total_elapsed']}`\n"
    elif data == "btn_help":
        response_text = (
            "❓ *Stopwatch Help*\n"
            "Use interactive buttons to manipulate the timer instance. State logs cleanly into history records when explicitly stopped."
        )
    elif data == "btn_about":
        response_text = (
            "ℹ️ *About StopwatchBot*\n"
            "• *Version:* `1.0.0` \n"
            "• *Stack:* Python 3.12, PTB v21\n"
            "• *Compliance:* Privacy secure (No private keys or data parsed outside application scopes)."
        )
        
    # Re-evaluate status variables post operational pipeline triggers
    new_row = database.get_stopwatch(user_id)
    new_status = new_row['status'] if new_row else 'STOPPED'
    
    await query.edit_message_text(
        text=escape_markdown(response_text),
        parse_mode="MarkdownV2",
        reply_markup=get_main_keyboard(new_status)
    )
