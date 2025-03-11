import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token
BOT_TOKEN = "7673094518:AAG0Sp3JSYBlPlgWffAIbaVsKeDy8YZpGd8"
bot = telebot.TeleBot(BOT_TOKEN)

# Admin ID
ADMIN_ID = 6043602577

# Global File Storage (Accessible by all users)
global_storage = {}

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # Check if user opened a file link
    if len(args) > 1 and args[1].startswith("file_"):
        file_code = args[1][5:]
        file_data = global_storage.get(file_code)

        if file_data:
            send_file(user_id, file_data)
        else:
            bot.send_message(user_id, "❌ File not found or expired.")
        return

    # Inline keyboard
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📁 My Storage", callback_data='my_storage'))
    markup.row(InlineKeyboardButton("💎 Subscription", callback_data='subscription'))
    markup.row(InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/CN_X_OWNER"))
    markup.row(InlineKeyboardButton("📢 Developer Channel", url="https://t.me/ChiragNetwork_930"))
    markup.row(InlineKeyboardButton("💽 Database Info", callback_data='database'))

    bot.send_message(user_id, "🚀 *Welcome to TeleCloudBot!*\n🔒 Securely save and share your files with unique links.",
                     reply_markup=markup, parse_mode='Markdown')

# File Upload and Link Generation
@bot.message_handler(content_types=["document", "photo", "video", "audio"])
def save_file(message):
    # Unique short file code
    file_code = str(abs(hash(str(message.message_id))))[:6]

    # Identify file type and get file_id
    file_id = None
    file_type = None

    if message.document:
        file_id = message.document.file_id
        file_type = 'document'
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
    elif message.audio:
        file_id = message.audio.file_id
        file_type = 'audio'

    if not file_id:
        bot.send_message(message.chat.id, "❌ Unsupported file type. Please try again!")
        return

    # Save file globally
    global_storage[file_code] = {
        "file_id": file_id,
        "file_type": file_type
    }

    # Generate file link
    bot_username = bot.get_me().username
    file_link = f"https://t.me/{bot_username}?start=file_{file_code}"

    # Confirming file saved
    bot.send_message(message.chat.id,
                     f"✅ *File saved successfully!*\n\n🔗 *File Link:* `{file_link}`\n\n📤 Share this link to access your file easily!",
                     parse_mode='Markdown')

# Function to send file
def send_file(chat_id, file_data):
    if file_data['file_type'] == 'document':
        bot.send_document(chat_id, file_data['file_id'])
    elif file_data['file_type'] == 'photo':
        bot.send_photo(chat_id, file_data['file_id'])
    elif file_data['file_type'] == 'video':
        bot.send_video(chat_id, file_data['file_id'])
    elif file_data['file_type'] == 'audio':
        bot.send_audio(chat_id, file_data['file_id'])

# Admin-Only Upgrade Command
@bot.message_handler(commands=['upgrade'])
def upgrade(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 You are not authorized to use this command.")
        return

    try:
        _, user_id, plan = message.text.split()
        user_id = int(user_id)
        bot.send_message(user_id, f"🎉 *Congratulations!* Your storage plan has been upgraded to *{plan}*! 🚀",
                         parse_mode='Markdown')
        bot.send_message(message.chat.id, f"✅ *User `{user_id}` successfully upgraded to {plan}.*",
                         parse_mode='Markdown')
    except ValueError:
        bot.send_message(message.chat.id,
                         "⚠️ *Usage:* `/upgrade <user_id> <plan>`\n💡 *Example:* `/upgrade 123456789 2GB`",
                         parse_mode='Markdown')

# Callbacks for Inline Buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'my_storage':
        if not global_storage:
            bot.send_message(call.from_user.id, "📂 Your storage is empty. Start uploading files now!")
        else:
            for code in global_storage:
                bot_username = bot.get_me().username
                file_link = f"https://t.me/{bot_username}?start=file_{code}"
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("🗑 Delete", callback_data=f"delete_{code}"),
                    InlineKeyboardButton("🔗 Get Link", url=file_link)
                )
                bot.send_message(call.from_user.id, f"📁 File Code: {code}", reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'subscription':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("💼 1GB Plan - ₹50", callback_data='plan_1gb'))
        markup.row(InlineKeyboardButton("📦 2GB Plan - ₹100", callback_data='plan_2gb'))
        markup.row(InlineKeyboardButton("📲 Contact Admin", url="https://t.me/CN_X_OWNER"))
        bot.send_message(call.from_user.id, "💎 *Choose a subscription plan or contact admin for custom plans.*",
                         reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'database':
        bot.send_message(call.from_user.id, "💽 *Database:* CR INNOVATIONS PVT LTD CRR CLOUD STORE V2",
                         parse_mode='Markdown')

    elif call.data.startswith("delete_"):
        code = call.data.split("_")[1]
        if code in global_storage:
            del global_storage[code]
            bot.send_message(call.from_user.id, f"🗑 *File `{code}` deleted successfully.*", parse_mode='Markdown')

# Polling the bot
bot.polling()