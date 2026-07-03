import asyncio
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, logger
import database
import handlers

def main():
    # Initialize the database and ensure schemas match perfectly
    database.init_db()
    
    # Python 3.14 event loop initialization patch
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        logger.info("No active event loop detected in thread. Allocating new loop context...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    logger.info("Initializing Telegram Core Application instance...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command mappings
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("history", handlers.history_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    
    # Unified Callback control surface router 
    application.add_handler(CallbackQueryHandler(handlers.handle_callback))
    
    logger.info("Bot execution loop initialized. Polling incoming packets...")
    application.run_polling()

if __name__ == '__main__':
    main()
