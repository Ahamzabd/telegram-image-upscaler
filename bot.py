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

# Color theme
COLORS = {
    "primary": "#6C63FF",  # Purple
    "secondary": "#FF6584",  # Pink
    "accent": "#42C0FB",  # Blue
    "success": "#4CAF50",  # Green
}

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
    
    # Check if the update is from callback or command
    if update.message:
        update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

def about(update: Update, context: CallbackContext) -> None:
    """Show about information"""
    query = update.callback_query
    query.answer()
    
    about_text = (
        f"✨ *About Free Image Upscaler Bot*\n\n"
        f"• *Version*: 1.0\n"
        f"• *Pricing*: Forever FREE! 🎉\n"
        f"• *Formats*: JPG, PNG, WEBP, BMP\n"
        f"• *Max Size*: 10MB\n\n"
        f"*How it works*:\n"
        f"1. Upload any image\n"
        f"2. Choose upscale quality (2x, 4x, 8x)\n"
        f"3. Get your enhanced image!\n\n"
        f"Enjoy crystal clear images without any watermarks or payments!"
    )
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        about_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def upscale_options(update: Update, context: CallbackContext) -> None:
    """Show upscaling options"""
    query = update.callback_query
    query.answer()
    
    options_text = (
        f"🖼 *Choose Upscale Quality*\n\n"
        f"Select how much you want to enhance your image quality:\n\n"
        f"• *2x* - Moderate enhancement\n"
        f"• *4x* - High quality enhancement\n"
        f"• *8x* - Maximum quality (may take longer)"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("2x Quality", callback_data='quality_2x'),
            InlineKeyboardButton("4x Quality", callback_data='quality_4x'),
        ],
        [
            InlineKeyboardButton("8x Quality", callback_data='quality_8x'),
            InlineKeyboardButton("⬅️ Back", callback_data='back_to_main'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        options_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def handle_image(update: Update, context: CallbackContext) -> None:
    """Handle incoming images"""
    if 'quality' not in context.user_data:
        update.message.reply_text(
            "⚠️ Please select upscale quality first using /upscale command!",
            parse_mode='Markdown'
        )
        return
    
    # Download the image
    photo_file = update.message.photo[-1].get_file()
    image_stream = BytesIO()
    photo_file.download(out=image_stream)
    image_stream.seek(0)
    
    # Process the image
    try:
        with Image.open(image_stream) as img:
            original_format = img.format or 'JPEG'  # Default to JPEG if format not detected
            original_size = img.size
            
            # Determine scale factor based on user selection
            scale_factor = {
                'quality_2x': 2,
                'quality_4x': 4,
                'quality_8x': 8
            }.get(context.user_data['quality'], 2)
            
            new_size = (original_size[0] * scale_factor, original_size[1] * scale_factor)
            
            # Upscale the image
            upscaled_img = img.resize(new_size, Image.LANCZOS)
            
            # Save to buffer
            output_buffer = BytesIO()
            upscaled_img.save(output_buffer, format=original_format, quality=95)
            output_buffer.seek(0)
            
            # Send the upscaled image
            update.message.reply_photo(
                photo=output_buffer,
                caption=f"✅ Successfully upscaled {scale_factor}x!\n"
                       f"Original: {original_size[0]}x{original_size[1]}\n"
                       f"Upscaled: {new_size[0]}x{new_size[1]}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        update.message.reply_text(
            "❌ Sorry, I couldn't process that image. Please try another one!",
            parse_mode='Markdown'
        )

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    query.answer()
    
    if query.data == 'upscale_options':
        upscale_options(update, context)
    elif query.data == 'about':
        about(update, context)
    elif query.data == 'back_to_main':
        start(update, context)
    elif query.data.startswith('quality_'):
        context.user_data['quality'] = query.data
        query.edit_message_text(
            f"🎉 *Great!* Now send me the image you want to upscale {query.data.replace('quality_', '').upper()}",
            parse_mode='Markdown'
        )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and update.message:
        update.message.reply_text(
            "😢 Sorry, something went wrong. Please try again later!",
            parse_mode='Markdown'
        )

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("upscale", upscale_options))
    
    # Register message handlers
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, handle_image))
    
    # Register callback handlers
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)

    # Start the Bot (for webhook deployment)
    # Comment this out for local testing
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://your-app-name.herokuapp.com/{TOKEN}"
    )
    
    # For local testing, uncomment this line:
    # updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
    updater.start_polling()  # Keep this line
