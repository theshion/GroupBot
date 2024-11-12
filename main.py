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
                        group_info["invite_link"] = f"𝖢𝗈𝗎𝗅𝖽 𝖭𝗈𝗍 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖨𝗇𝗏𝗂𝗋𝖾 𝖫𝗂𝗇𝗄 : {e}"
                    try:
                        async for message in user_client.get_chat_history(dialog.chat.id, limit=1, offset_id=0):
                            group_info["creation_date"] = message.date.strftime("%Y/%m/%d")
                            group_info["creation_time"] = message.date.strftime("%H:%M:%S")
                            break
                    except Exception as e:
                        group_info["creation_date"] = f"𝖢𝗈𝗎𝗅𝖽 𝖭𝗈𝗍 𝖣𝖾𝗍𝖾𝗋𝗆𝗂𝗇𝖾 𝖢𝗋𝖾𝖺𝗍𝗂𝗈𝗇 𝖣𝖺𝗍𝖾 𝖠𝗇𝖽 𝖳𝗂𝗆𝖾 : {e}"
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
                        group_info["media_count"] = f"𝖢𝗈𝗎𝗅𝖽 𝖭𝗈𝗍 𝖢𝗈𝗎𝗇𝗍 𝖬𝖾𝖽𝗂𝖺 : {e}"
                        group_info["message_count"] = f"𝖢𝗈𝗎𝗅𝖽 𝖭𝗈𝗍 𝖢𝗈𝗎𝗇𝗍 𝖬𝖾𝗌𝗌𝗀𝖺𝖾 : {e}"
                    owned_groups.append(group_info)
            except Exception as e:
                print(f"𝖢𝗈𝗎𝗅𝖽 𝖭𝗈𝗍 𝖥𝖾𝗍𝖼𝗁 𝖬𝖾𝗆𝖻𝖾𝗋𝗌 𝖣𝖾𝗍𝖺𝗂𝗅𝗌 𝖥𝗈𝗋 {dialog.chat.title} : {e}")
    if owned_groups:
        response_message = "**𝖦𝗋𝗈𝗎𝗉 𝖨𝗇𝖿𝗈 :**\n\n"
        for group in owned_groups:
            response_message += (
                f"• 𝖦𝗋𝗈𝗎𝗉 𝖳𝗂𝗍𝗅𝖾 : {group['title']}\n"
                f"• 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾 : {group['username']}\n"
                f"• 𝖬𝖾𝗆𝖻𝖾𝗋𝗌 𝖢𝗈𝗎𝗇𝗍 : {group['members_count']}\n"
                f"• 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄 : [Click Here]({group['invite_link']})\n"
                f"• 𝖢𝗋𝖾𝖺𝗍𝗂𝗈𝗇 𝖣𝖺𝗍𝖾 : {group['creation_date']}\n"
                f"• 𝖢𝗋𝖾𝖺𝗍𝗂𝗈𝗇 𝖳𝗂𝗆𝖾 : {group['creation_time']}\n"
                f"• 𝖬𝖾𝖽𝗂𝖺 𝖢𝗈𝗎𝗇𝗍 : {group['media_count']}\n"
                f"• 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖢𝗈𝗎𝗇𝗍 : {group['message_count']}\n\n"
            )
    else:
        response_message = "𝖴𝗌𝖾𝗋 𝖣𝗈𝖾𝗌 𝖭𝗈𝗍 𝖮𝗐𝗇 𝖠𝗇𝗒 𝖦𝗋𝗈𝗎𝗉𝗌."
    await xemishra.send_message(chat_id=user_id, text=response_message)

@xemishra.on_message(filters.command("check"))
async def check_user_client(bot, message):
    if len(message.command) < 2:
        await message.reply("𝖯𝗅𝖾𝖺𝗌𝖾 𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖠 𝖯𝗒𝗋𝗈𝗀𝗋𝖺𝗆 𝖵2 𝖲𝖾𝗌𝗌𝗂𝗈𝗇 𝖲𝗍𝗋𝗂𝗇𝗀 : /check <session string>")
        return
    session_string = message.command[1]
    user_id = message.from_user.id
    x = await xemishra.send_message(chat_id=user_id, text="𝖯𝗋𝗈𝖼𝖼𝖾𝗌𝗌𝗂𝗇𝗀...")
    try:
        user_client = Client(name="UserBot", api_id=api_id, api_hash=api_hash, session_string=session_string)
        await user_client.start()
        await get_owned_groups(user_client, user_id)
        await x.delete()
        await user_client.stop()
    except SessionPasswordNeeded:
        sessions_requiring_2sv[user_id] = session_string
        await bot.send_message(chat_id=user_id, text="𝖳𝗁𝗂𝗌 𝖲𝖾𝗌𝗌𝗂𝗈𝗇 𝖱𝖾𝗊𝗎𝗂𝗋𝖾𝗌 𝖠 2𝖲𝖵 𝖯𝖺𝗌𝗌𝗐𝗈𝗋𝖽. 𝖯𝗅𝖾𝖺𝗌𝖾 𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖨𝗍 𝖴𝗌𝗂𝗇𝗀 : /pass <password>")
    except AuthKeyUnregistered:
        await bot.send_message(chat_id=user_id, text="𝖳𝗁𝖾 𝖯𝗋𝗈𝗏𝗂𝖽𝖾𝖽 𝖲𝖾𝗌𝗌𝗂𝗈𝗇 𝖨𝗌 𝖤𝗑𝗉𝗂𝗋𝖾𝖽 𝖮𝗋 𝖨𝗇𝗏𝖺𝗅𝗂𝖽.")
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f"𝖠𝗇 𝖤𝗋𝗋𝗈𝗋 𝖮𝖼𝖼𝗎𝗋𝗋𝖾𝖽 : {e}")

@xemishra.on_message(filters.command("pass"))
async def handle_2sv(bot, message):
    user_id = message.from_user.id
    if user_id not in sessions_requiring_2sv:
        await message.reply("𝖭𝗈 𝖲𝖾𝗌𝗌𝗂𝗈𝗇 𝖨𝗌 𝖶𝖺𝗍𝗂𝗇𝗀 𝖥𝗈𝗋 𝖠 2𝖲𝖵 𝖯𝖺𝗌𝗌𝗐𝗈𝗋𝖽.")
        return
    if len(message.command) < 2:
        await message.reply("𝖯𝗅𝖾𝖺𝗌𝖾 𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖳𝗁𝖾 2𝖲𝖵 𝖯𝖺𝗌𝗌𝗐𝗈𝗋𝖽 𝖴𝗌𝗂𝗇𝗀 : /pass <password>")
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
        await bot.send_message(chat_id=user_id, text=f"2𝖲𝖵 𝖫𝗈𝗀𝗂𝗇 𝖥𝖺𝗂𝗅𝖾𝖽 : {e}")

xemishra.run()
print("𝖦𝗋𝗈𝗎𝗉𝖡𝗈𝗍 𝖲𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 !!")
