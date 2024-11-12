import json
from telebot import TeleBot, types
from pyrogram import Client
import asyncio

# Bot Token and Pyrogram API details
API_TOKEN = "7632024645:AAEtZ0I7551DPnqe1nzsf6nZs2NPxdEpFCA"
api_id = '20787644'  # From https://my.telegram.org
api_hash = '9dada820698e8a5fdd5e6cc78fac8567'  # From https://my.telegram.org

bot = TeleBot(API_TOKEN)

# Temporary session storage
sessions = {}

# Path to save session data (using JSON)
SESSION_FILE_PATH = 'sessions.json'

# Load saved sessions
def load_sessions():
    try:
        with open(SESSION_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save sessions
def save_sessions(data):
    with open(SESSION_FILE_PATH, 'w') as f:
        json.dump(data, f)

# Start command: Show options
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Add Session")
    button2 = types.KeyboardButton("Start Check")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "Welcome! Please choose an option:", reply_markup=markup)

# Handle 'Add Session' button
@bot.message_handler(func=lambda message: message.text == "Add Session")
def add_session(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Please send your Pyrogram v2 session string.")
    sessions[user_id] = "add_session"  # Mark user for session input

# Handle session input from the user
@bot.message_handler(func=lambda message: True)
def handle_session_input(message):
    user_id = message.from_user.id

    if user_id in sessions and sessions[user_id] == "add_session":
        session_data = message.text.strip()

        # Check if session is valid
        try:
            asyncio.run(check_session(message, session_data))
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {str(e)}")
        finally:
            del sessions[user_id]  # Clear session input state

# Check session validity and save it
async def check_session(message, session_data):
    client = Client("UserBot", api_id=api_id, api_hash=api_hash, session_string=session_data)
    
    try:
        await client.start()  # Try starting the client with the session

        # Validate by fetching user details
        me = await client.get_me()
        bot.send_message(message.chat.id, f"Session validated successfully! Welcome, {me.first_name}.")

        # Save session to file
        saved_sessions = load_sessions()
        saved_sessions[str(message.from_user.id)] = session_data
        save_sessions(saved_sessions)
        await client.stop()
    except Exception as e:
        raise Exception(f"Invalid session or session expired. Error: {str(e)}")

# Handle 'Start Check' button
@bot.message_handler(func=lambda message: message.text == "Start Check")
def start_check(message):
    user_id = message.from_user.id

    # Load saved session for user
    saved_sessions = load_sessions()
    session_data = saved_sessions.get(str(user_id))

    if session_data:
        asyncio.run(check_groups(message, session_data))
    else:
        bot.send_message(message.chat.id, "No valid session found. Please add a session first.")

# Fetch and list the groups using the session
async def check_groups(message, session_data):
    client = Client("GroupBot", api_id=api_id, api_hash=api_hash, session_string=session_data)

    try:
        await client.start()
        
        # Fetch the user's chat list
        chats = await client.get_chats()
        groups = [chat.title for chat in chats if chat.type == "supergroup"]

        if groups:
            bot.send_message(message.chat.id, "You are part of the following groups:\n" + "\n".join(groups))
        else:
            bot.send_message(message.chat.id, "You are not part of any supergroups.")
        
        await client.stop()
    except Exception as e:
        bot.send_message(message.chat.id, f"Error fetching groups: {str(e)}")

# Start the bot
bot.polling(none_stop=True)
