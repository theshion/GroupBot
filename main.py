from pyrogram import Client, enums, filters
from pyrogram.errors import AuthKeyUnregistered, SessionPasswordNeeded

bot_token = "7952485026:AAFdD01FxulJUukzrP-ha-t0ABXGqQdbkQk"
api_id = 28102624
api_hash = "4e03913f9a576278ed4dbcdf7073e1b0"

xemishra = Client("GroupBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

sessions_requiring_2sv = {}

async def get_owned_groups(user_client, user_id):
    owned_groups = []
    Me = await user_client.get_me()
    async for dialog in user_client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            try:
                user_s = await dialog.chat.get_member(Me.id)
                if user_s.status == enums.ChatMemberStatus.OWNER:
                    group_info = {
                        "title": dialog.chat.title,
                        "username": f"@{dialog.chat.username}" if dialog.chat.username else "No username",
                        "members_count": dialog.chat.members_count if dialog.chat.members_count else "Unknown"
                    }
                    try:
                        invite_link = await user_client.export_chat_invite_link(dialog.chat.id)
                        group_info["invite_link"] = invite_link
                    except Exception as e:
                        group_info["invite_link"] = f"Could not generate invite link: {e}"
                    try:
                        async for message in user_client.get_chat_history(dialog.chat.id, limit=1, offset_id=0):
                            group_info["creation_date"] = message.date.strftime("%Y-%m-%d %H:%M:%S")
                            break
                    except Exception as e:
                        group_info["creation_date"] = f"Could not determine creation date: {e}"
                    media_count = 0
                    message_count = 0
                    try:
                        async for message in user_client.get_chat_history(dialog.chat.id):
                            message_count += 1
                            if message.media:
                                media_count += 1
                        group_info["media_count"] = media_count
                        group_info["message_count"] = message_count
                    except Exception as e:
                        group_info["media_count"] = f"Could not count media: {e}"
                        group_info["message_count"] = f"Could not count messages: {e}"
                    owned_groups.append(group_info)
            except Exception as e:
                print(f"Could not fetch member details for {dialog.chat.title}: {e}")
    if owned_groups:
        response_message = "Owned Groups:\n\n"
        for group in owned_groups:
            response_message += (
                f"**Group Title:** {group['title']}\n"
                f"**Username:** {group['username']}\n"
                f"**Members Count:** {group['members_count']}\n"
                f"**Invite Link:** {group['invite_link']}\n"
                f"**Creation Date:** {group['creation_date']}\n"
                f"**Media Count:** {group['media_count']}\n"
                f"**Message Count:** {group['message_count']}\n"
                "------------------------------\n"
            )
    else:
        response_message = "User does not own any groups."
    await xemishra.send_message(chat_id=user_id, text=response_message)

@xemishra.on_message(filters.command("check"))
async def check_user_client(bot, message):
    if len(message.command) < 2:
        await message.reply("Please provide a session string.")
        return
    session_string = message.command[1]
    user_id = message.from_user.id
    try:
        user_client = Client(name="UserBot", api_id=api_id, api_hash=api_hash, session_string=session_string)
        await user_client.start()
        await get_owned_groups(user_client, user_id)
        await user_client.stop()
    except SessionPasswordNeeded:
        sessions_requiring_2sv[user_id] = session_string
        await bot.send_message(chat_id=user_id, text="This session requires a 2SV password. Please provide it using `/2sv <password>`.")
    except AuthKeyUnregistered:
        await bot.send_message(chat_id=user_id, text="The provided session is expired or invalid.")
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f"An error occurred: {e}")

@xemishra.on_message(filters.command("2sv"))
async def handle_2sv(bot, message):
    user_id = message.from_user.id
    if user_id not in sessions_requiring_2sv:
        await message.reply("No session is waiting for a 2SV password.")
        return
    if len(message.command) < 2:
        await message.reply("Please provide the 2SV password.")
        return
    password = message.command[1]
    session_string = sessions_requiring_2sv[user_id]
    try:
        user_client = Client(name="UserBot", api_id=api_id, api_hash=api_hash, session_string=session_string)
        await user_client.start(password=password)
        await get_owned_groups(user_client, user_id)
        await user_client.stop()
        del sessions_requiring_2sv[user_id]
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f"2SV login failed: {e}")

xemishra.run()
