import asyncio
import os
import shutil
from pyrogram import filters
from Opus import app
from Opus.misc import SUDOERS
from datetime import datetime


CLEAN_INTERVAL = 1800  
TARGET_DIRS = ["downloads", "cache"]  import asyncio
import os
import shutil
from pyrogram import filters
from Opus import app
from Opus.misc import SUDOERS
from datetime import datetime


CLEAN_INTERVAL = 1800  
TARGET_DIRS = ["downloads", "cache"]  
LOG_FILE = "cleaner.log"  

async def log_activity(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {message}\n")

async def nuke_directories():
    while True:
        try:
            for dir_path in TARGET_DIRS:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path) 
                    os.makedirs(dir_path)  
                    await log_activity(f"☢️ ɴᴜᴋᴇᴅ: {dir_path}")
                    print(f"☢️ ᴅᴇʟᴇᴛᴇᴅ: {dir_path}")

            print("✅ ᴀᴜᴛᴏ-ᴄʟᴇᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!")
        except Exception as e:
            await log_activity(f"💥 ᴇʀʀᴏʀ: {str(e)}")
            print(f"⚠️ ᴄʟᴇᴀɴᴇʀ ᴇʀʀᴏʀ: {e}")

        await asyncio.sleep(CLEAN_INTERVAL)


@app.on_message(filters.command("start_cleaner") & SUDOERS)
async def start_nuker(_, message):
    asyncio.create_task(nuke_directories())
    await message.reply_text(
        "🛁 <b>ꜱᴛᴀʀᴛᴇᴅ ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ</b>\n\n"
        f"• <b>ᴛᴀʀɢᴇᴛꜱ:</b> <code>{', '.join(TARGET_DIRS)}</code>\n"
        f"• <b>ꜰʀᴇQᴜᴇɴᴄʏ:</b> <code>{CLEAN_INTERVAL//60} ᴍɪɴᴜᴛᴇꜱ</code>\n"
        "• <b>ᴍᴏᴅᴇ:</b> <code>ɴᴏ ᴇxᴄᴇᴘᴛɪᴏɴꜱ, ꜰᴜʟʟ ᴡɪᴘᴇ</code>",
    )

@app.on_message(filters.command("clean_now") & SUDOERS)
async def trigger_nuke(_, message):
    try:
        for dir_path in TARGET_DIRS:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                os.makedirs(dir_path)
        await message.reply_text("💥 <b>ᴍᴀɴᴜᴀʟ ᴄʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇ!</b>")
    except Exception as e:
        await message.reply_text(f"❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{e}</code>")

@app.on_message(filters.command("cleaner_status") & SUDOERS)
async def nuker_status(_, message):
    await message.reply_text(
        "📊 <b>ᴄʟᴇᴀɴᴇʀ ꜱᴛᴀᴛᴜꜱ</b>\n\n"
        f"• <b>ʀᴜɴɴɪɴɢ:</b> <code>ʏᴇꜱ</code>\n"
        f"• <b>ɴᴇxᴛ ᴄʟᴇᴀɴ ɪɴ:</b> <code>{CLEAN_INTERVAL//60} ᴍɪɴᴜᴛᴇꜱ</code>\n"
        f"• <b>ᴛᴀʀɢᴇᴛꜱ:</b> <code>{', '.join(TARGET_DIRS)}</code>\n"
        "• <b>ᴡᴀʀɴɪɴɢ:</b> <code>ᴛʜɪꜱ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴇᴠᴇʀʏᴛʜɪɴɢ ɪɴ ᴛᴀʀɢᴇᴛ ꜰᴏʟᴅᴇʀꜱ!</code>"
    )
LOG_FILE = "cleaner.log"  

async def log_activity(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {message}\n")

async def nuke_directories():
    while True:
        try:
            for dir_path in TARGET_DIRS:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path) 
                    os.makedirs(dir_path)  
                    await log_activity(f"☢️ ɴᴜᴋᴇᴅ: {dir_path}")
                    print(f"☢️ ᴅᴇʟᴇᴛᴇᴅ: {dir_path}")

            print("✅ ᴀᴜᴛᴏ-ᴄʟᴇᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!")
        except Exception as e:
            await log_activity(f"💥 ᴇʀʀᴏʀ: {str(e)}")
            print(f"⚠️ ᴄʟᴇᴀɴᴇʀ ᴇʀʀᴏʀ: {e}")

        await asyncio.sleep(CLEAN_INTERVAL)


@app.on_message(filters.command("start_cleaner") & SUDOERS)
async def start_nuker(_, message):
    asyncio.create_task(nuke_directories())
    await message.reply_text(
        "🛁 **ꜱᴛᴀʀᴛᴇᴅ ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ**\n\n"
        f"• **ᴛᴀʀɢᴇᴛꜱ:** `{', '.join(TARGET_DIRS)}`\n"
        f"• **ꜰʀᴇQᴜᴇɴᴄʏ:** `{CLEAN_INTERVAL//60} ᴍɪɴᴜᴛᴇꜱ`\n"
        "• **ᴍᴏᴅᴇ:** `ɴᴏ ᴇxᴄᴇᴘᴛɪᴏɴꜱ, ꜰᴜʟʟ ᴡɪᴘᴇ`"
    )

@app.on_message(filters.command("clean_now") & SUDOERS)
async def trigger_nuke(_, message):
    try:
        for dir_path in TARGET_DIRS:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                os.makedirs(dir_path)
        await message.reply_text("💥 **ᴍᴀɴᴜᴀʟ ᴄʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇ!**")
    except Exception as e:
        await message.reply_text(f"❌ **ꜰᴀɪʟᴇᴅ:** `{e}`")

@app.on_message(filters.command("cleaner_status") & SUDOERS)
async def nuker_status(_, message):
    await message.reply_text(
        "📊 **ᴄʟᴇᴀɴᴇʀ ꜱᴛᴀᴛᴜꜱ**\n\n"
        f"• **ʀᴜɴɴɪɴɢ:** `ʏᴇꜱ`\n"
        f"• **ɴᴇxᴛ ᴄʟᴇᴀɴ ɪɴ:** `{CLEAN_INTERVAL//60} ᴍɪɴᴜᴛᴇꜱ`\n"
        f"• **ᴛᴀʀɢᴇᴛꜱ:** `{', '.join(TARGET_DIRS)}`\n"
        "• **ᴡᴀʀɴɪɴɢ:** `ᴛʜɪꜱ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴇᴠᴇʀʏᴛʜɪɴɢ ɪɴ ᴛᴀʀɢᴇᴛ ꜰᴏʟᴅᴇʀꜱ!`"
    )
