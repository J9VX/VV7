from pyrogram import filters
from pyrogram.types import Message

from Opus import app
from Opus.misc import SUDOERS
from Opus.utils.database import autoend_off, autoend_on


@app.on_message(filters.command("autoend") & SUDOERS)
async def auto_end_stream(_, message: Message):
    usage = "ᴇxᴀᴍᴘʟᴇ:\n\n/ᴀᴜᴛᴏᴇɴᴅ [ᴇɴᴀʙʟᴇ|ᴅɪsᴀʙʟᴇ|ɪɴsᴛᴀɴᴛ]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    
    state = message.text.split(None, 1)[1].strip().lower()
    
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "ᴀᴜᴛᴏ ᴇɴᴅ sᴛʀᴇᴀᴍ ᴇɴᴀʙʟᴇᴅ.\n\n"
            "ᴀssɪsᴛᴀɴᴛ ᴡɪʟʟ ʟᴇᴀᴠᴇ ᴡʜᴇɴ ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ ᴀғᴛᴇʀ sᴏᴍᴇ ᴛɪᴍᴇ."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("ᴀᴜᴛᴏ ᴇɴᴅ sᴛʀᴇᴀᴍ ᴅɪsᴀʙʟᴇᴅ.")
    elif state == "instant":
        await autoend_on()
        await message.reply_text(
            "ɪɴsᴛᴀɴᴛ ᴀᴜᴛᴏ ᴇɴᴅ ᴇɴᴀʙʟᴇᴅ!\n\n"
            "ᴀssɪsᴛᴀɴᴛ ᴡɪʟʟ ʟᴇᴀᴠᴇ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ᴡʜᴇɴ ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ."
        )
    else:
        await message.reply_text(usage)
