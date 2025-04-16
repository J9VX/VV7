import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
import config
from Opus import app
from Opus.misc import _boot_
from Opus.plugins.sudo.sudoers import sudoers_list
from Opus.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Opus.utils.decorators.language import LanguageStart
from Opus.utils.formatters import get_readable_time
from Opus.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


async def send_combined_message(message: Message, text: str, photo_url: str, reply_markup=None):
    """Send a single message with caption first, then image"""
    # First send the text as a message
    sent_message = await message.reply_text(
        text=text,
        reply_markup=reply_markup
    )
    
    # Then reply to that message with the image
    if photo_url:
        await sent_message.reply_photo(
            photo=photo_url,
            reply_to_message_id=sent_message.id
        )
    return sent_message


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            await send_combined_message(
                message,
                text=_["help_1"].format(config.SUPPORT_CHAT),
                photo_url=config.START_IMG_URL,
                reply_markup=keyboard
            )
            return
            
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<blockquote><b>» <a href='https://t.me/{message.from_user.username}'>User</a> just started the bot to check sudo list</b>\n<b>User ID:</b> <code>{message.from_user.id}</code></blockquote>",
                    disable_web_page_preview=True
                )
            return
            
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            
            try:
                results = VideosSearch(query, limit=1)
                result = (await results.next())["result"][0]
                
                searched_text = _["start_6"].format(
                    result["title"],
                    result["duration"],
                    result["viewCount"]["short"],
                    result["publishedTime"],
                    result["channel"]["link"],
                    result["channel"]["name"],
                    app.mention
                )
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=result["link"]),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ]
                ])
                
                await m.delete()
                await send_combined_message(
                    message,
                    text=searched_text,
                    photo_url=result["thumbnails"][0]["url"].split("?")[0],
                    reply_markup=keyboard
                )
                
                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=f"<blockquote><b>» <a href='https://t.me/{message.from_user.username}'>User</a> checked track info</b>\n<b>User ID:</b> <code>{message.from_user.id}</code></blockquote>",
                        disable_web_page_preview=True
                    )
                    
            except Exception as e:
                await m.edit_text(_["start_7"].format(e))
            return
            
    # Default start message for private chats
    await send_combined_message(
        message,
        text=_["start_2"].format(message.from_user.mention, app.mention),
        photo_url=config.START_IMG_URL,
        reply_markup=InlineKeyboardMarkup(private_panel(_))
    )
    
    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"<blockquote><b>» <a href='https://t.me/{message.from_user.username}'>User</a> started the bot</b>\n<b>User ID:</b> <code>{message.from_user.id}</code></blockquote>",
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    uptime = int(time.time() - _boot_)
    await send_combined_message(
        message,
        text=_["start_1"].format(app.mention, get_readable_time(uptime)),
        photo_url=config.START_IMG_URL,
        reply_markup=InlineKeyboardMarkup(start_panel(_))
    )
    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
                return
                
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                await send_combined_message(
                    message,
                    text=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    photo_url=config.START_IMG_URL,
                    reply_markup=InlineKeyboardMarkup(start_panel(_))
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
                
        except Exception as ex:
            print(f"Error in welcome handler: {ex}")
