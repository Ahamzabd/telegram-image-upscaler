import os
import logging
from io import BytesIO
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = "7872559568:AAHQo3xJ1g8jexYNd8KgfTtagD_OMGjwuNs"
PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_URL = "https://your-actual-domain.com"  # CHANGE THIS

def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message with colorful buttons"""
    keyboard = [
        [InlineKeyboardButton("🚀 Upscale Image", callback_data='upscale_options')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')],
        [InlineKeyboardButton("🌟 Rate Us", url="https://t.me/")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🌈 *Welcome to Free Image Upscaler Bot!*\n\n"
        f"Upload any image (JPG/PNG/WEBP) and I'll enhance its quality for you - "
        f"*completely FREE forever!* 💖\n\n"
        f"Click below to get started:"
    )
    
    if update.message:
        update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# [Keep all your other functions exactly the same...]

def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("upscale", upscale_options))
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, handle_image))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_error_handler(error_handler)

    # Deployment mode selection
    if os.environ.get('ENVIRONMENT') == 'PRODUCTION':
        # Webhook for production
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
        logger.info("Bot running in webhook mode")
    else:
        # Polling for development
        updater.start_polling()
        logger.info("Bot running in polling mode")
        
        # Display local access information
        try:
            public_ip = requests.get('https://api.ipify.org').text
            logger.info(f"Public URL: https://t.me/your_bot_username")
            logger.info(f"Local URL: http://{public_ip}:{PORT}")
        except:
            logger.warning("Couldn't fetch public IP")

    updater.idle()

if __name__ == '__main__':
    main()
