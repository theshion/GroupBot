import json
from telebot import TeleBot, types
import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import Message

# Define your bot token
API_TOKEN = "7632024645:AAEtZ0I7551DPnqe1nzsf6nZs2NPxdEpFCA"
api_id = '20787644'  # From https://my.telegram.org
api_hash = '9dada820698e8a5fdd5e6cc78fac8567'  # From https://my.telegram.org

bot = TeleBot(API_TOKEN)

# Store user session states temporarily
sessions = {}  # Will store user session actions
check_with_sessions = {}  # Will store validated sessions for users

# Path to save session data (using a JSON file)
SESSION_FILE_PATH = 'sessions.json'

# Load saved sessions from the JSON file (if any)
def load_sessions():
    try:
        with open(SESSION_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save sessions to the JSON file
def save_sessions(data):
    with open(SESSION_FILE_PATH, 'w') as f:
        json.dump(data, f)

# Handle start command and show the buttons
@bot.message_handler(commands=['start'])
def send_start_message(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton('Add Session')
    button2 = types.KeyboardButton('Start Check')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "Welcome! Please choose an action below:", reply_markup=markup)

# Button press handler for adding session
@bot.message_handler(func=lambda message: message.text == "Add Session")
def handle_add_session(message):
    user_id = message.from_user.id
    bot.reply_to(message, "Send your *Pyrogram v2 session string* now.", parse_mode="Markdown")
    sessions[user_id] = "add"  # Mark that the user is in the process of adding a session

# Handle all messages for adding session string
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    user_id = message.from_user.id

    if user_id in sessions and sessions[user_id] == "add":
        session_data = text  # User's v2 session string
        try:
            asyncio.run(check_session(message, user_id, session_data))  # Validate the session
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")
        del sessions[user_id]  # Remove the session action flag

# Validate and save session string
async def check_session(message, user_id, session_data):
    try:
        # Create a Pyrogram client with the provided session string
        client = Client("UserBot", api_id=api_id, api_hash=api_hash, session_string=session_data)
        await client.start()

        # Check if the user is authorized
        if not await client.is_user_authorized():
            raise Exception("Session expired ❌")

        # Save the session string if it's valid
        saved_sessions = load_sessions()
        saved_sessions[f"session_{user_id}"] = session_data
        save_sessions(saved_sessions)  # Save updated sessions to file
        check_with_sessions[user_id] = session_data  # Store the session for later use
        bot.reply_to(message, "Session saved ✅")

        await client.stop()  # Stop the client after usage
    except Exception as e:
        bot.reply_to(message, f"Session is invalid or expired ❌\nError: {str(e)}")

# Button press handler for checking session and performing actions
@bot.message_handler(func=lambda message: message.text == "Start Check")
def start_check(message):
    user_id = message.from_user.id
    try:
        # Get the saved session for the user
        saved_sessions = load_sessions()
        session_data = saved_sessions.get(f"session_{user_id}")
        if not session_data:
            bot.reply_to(message, "No session found! Please add a valid session using 'Add Session' button.")
            return
        
        # Perform the group check operation using the saved session
        asyncio.run(check_groups(message, session_data))
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Function to check group info using the session string
async def check_groups(message, session_data):
    try:
        # Use the saved session string to check group details
        client = Client("GroupCheckBot", api_id=api_id, api_hash=api_hash, session_string=session_data)
        await client.start()

        # Example: Retrieve the user's chat groups (can be customized)
        chats = await client.get_chats()  # Get the user's chat list
        group_names = [chat.title for chat in chats if chat.type == "supergroup"]  # Filter supergroups

        if group_names:
            bot.reply_to(message, "You are part of the following groups:\n" + "\n".join(group_names))
        else:
            bot.reply_to(message, "You are not part of any groups.")
        
        await client.stop()  # Stop the client after usage
    except Exception as e:
        bot.reply_to(message, f"Error occurred while checking groups: {str(e)}")

# Start the bot polling
bot.polling(none_stop=True)
