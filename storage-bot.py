import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# 🔐 Bot config
API_ID = 23079581
API_HASH = "bdaa3ca7a3789231b5488a594cc74a98"
BOT_TOKEN = "7680233688:AAEpT-gz0m1bYmEFeTofqXOQasmc9UIgNk8"
CHANNEL_USERNAME = "graficsy6"
FORCE_JOIN_CHANNEL = "moddingmaniaaa"
BOT_USERNAME = "Sheydvwhebbot"
VIP_USER_IDS = [7238861060]
UPLOAD_LOG = "upload_limits.json"

app = Client("Sheydvwhebbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def load_uploads():
    try:
        with open(UPLOAD_LOG, "r") as f:
            return json.load(f)
    except:
        return {}

def save_uploads(data):
    with open(UPLOAD_LOG, "w") as f:
        json.dump(data, f)

def check_upload_allowed(user_id: str) -> bool:
    if int(user_id) in VIP_USER_IDS:
        return True
    uploads = load_uploads()
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in uploads or uploads[user_id].get("date") != today:
        uploads[user_id] = {"date": today, "count": 0}
    if uploads[user_id]["count"] >= 6:
        return False
    uploads[user_id]["count"] += 1
    save_uploads(uploads)
    return True

async def is_user_joined(user_id):
    try:
        member = await app.get_chat_member(FORCE_JOIN_CHANNEL, user_id)
        return member.status not in ["kicked", "left"]
    except:
        return False

async def send_force_join_buttons(message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{FORCE_JOIN_CHANNEL}")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify_join")]
    ])
    await message.reply_text(
        "🚫 **Access Denied!**\n\n"
        "> You must **join our official channel** to use this bot.\n\n"
        "🔗 **Step 1:** [Join 𝙈𝙤𝙙𝙙𝙞𝙣𝙜 𝙈𝙖𝙣𝙞𝙖](https://t.me/moddingmaniaaa)\n"
        "✅ **Step 2:** Press the **\"Verify\"** button below after joining.\n\n"
        "_Only verified members can use this bot._",
        reply_markup=buttons,
        disable_web_page_preview=True
    )

@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "verify_join":
        if await is_user_joined(user_id):
            await callback_query.message.edit_text("✅ Verification successful! You're now allowed to use the bot.\n\nSend me a file to get started.")
        else:
            await callback_query.message.edit_text(
                "❌ You haven't joined the channel yet!\n\n🔗 Please join [𝙈𝙤𝙙𝙙𝙞𝙣𝙜 𝙈𝙖𝙣𝙞𝙖](https://t.me/moddingmaniaaa) first, then press Verify again.",
                disable_web_page_preview=True
            )

@app.on_message(filters.private & (
    filters.document | filters.photo | filters.video |
    filters.audio | filters.voice | filters.animation
))
async def handle_upload(client, message: Message):
    uid = message.from_user.id

    if not await is_user_joined(uid):
        return await send_force_join_buttons(message)

    uid_str = str(uid)
    if not check_upload_allowed(uid_str):
        await message.reply_text("⚠️ You've exceeded your 6-file daily upload limit.\n📩 Contact @moddingmaniaaa for more access.")
        return

    reply = await message.reply_text("📤 Uploading to channel...")

    try:
        sent = await message.forward(chat_id=f"@{CHANNEL_USERNAME}")
        link = f"https://t.me/{BOT_USERNAME}?start={sent.id}"
        await reply.edit(
            f"✅ Upload successful!\n🔗 File link:\n{link}"
        )
    except Exception as e:
        await reply.edit(f"❌ Upload failed:\n`{e}`")

@app.on_message(filters.command("start") & filters.private)
async def return_file(client, message: Message):
    uid = message.from_user.id

    if not await is_user_joined(uid):
        return await send_force_join_buttons(message)

    parts = message.text.strip().split()
    if len(parts) == 2 and parts[1].isdigit():
        msg_id = int(parts[1])
        try:
            file = await client.get_messages(chat_id=f"@{CHANNEL_USERNAME}", message_ids=msg_id)
            if not file or (not file.document and not file.photo and not file.video and not file.audio):
                raise ValueError("File no longer exists.")
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=f"@{CHANNEL_USERNAME}",
                message_id=msg_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📩 Share Bot", switch_inline_query="")]
                ])
            )
        except Exception as e:
            await message.reply_text(
                "❌ The file is no longer in the server or has been deleted by Owner.\n\n📩 Contact: @moddingmaniaaa"
            )
    else:
        await message.reply_text("👋 Send me any file — I'll upload it to the telegram server and give you a return link.")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()