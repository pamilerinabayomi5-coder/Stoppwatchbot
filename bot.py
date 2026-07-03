from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, logger
import database
import handlers

def main():
    # Initialize the database and ensure schemas match perfectly
    database.init_db()
    
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
