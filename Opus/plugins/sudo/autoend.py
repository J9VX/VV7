import asyncio
from pyrogram import filters
from pyrogram.types import Message
from Opus import app  # Only import the app which should be available
from Opus.misc import SUDOERS
from Opus.utils.database import autoend_off, autoend_on

# Global variable to track autoend status
AUTOEND_ENABLED = True

async def auto_leave_checker():
    """Background task to check and leave empty voice chats"""
    while True:
        if AUTOEND_ENABLED:
            try:
                # Get all active voice chats using Pyrogram's raw API
                async for dialog in app.get_dialogs():
                    if dialog.chat.type in ["group", "supergroup"]:
                        try:
                            # Check if we're in a voice chat in this group
                            call = await app.get_group_call(dialog.chat.id)
                            if call:
                                # Get call participants
                                participants = await app.get_group_call_participants(dialog.chat.id)
                                
                                # Count real participants (excluding the bot)
                                real_participants = [
                                    p for p in participants 
                                    if not p.user.is_self and not p.joined_by.is_self
                                ]
                                
                                if len(real_participants) == 0:
                                    # Wait for confirmation period
                                    await asyncio.sleep(30)
                                    
                                    # Recheck after delay
                                    participants = await app.get_group_call_participants(dialog.chat.id)
                                    real_participants = [
                                        p for p in participants 
                                        if not p.user.is_self and not p.joined_by.is_self
                                    ]
                                    
                                    if len(real_participants) == 0:
                                        await app.leave_group_call(dialog.chat.id)
                                        await app.send_message(
                                            dialog.chat.id,
                                            "⚠️ Left voice chat due to inactivity (no listeners detected)."
                                        )
                        except Exception as e:
                            # Skip if there's no call or other error
                            continue
            except Exception as e:
                print(f"Autoend checker error: {e}")
        
        # Check every 20 seconds
        await asyncio.sleep(20)

@app.on_message(filters.command("autoend") & SUDOERS)
async def auto_end_stream(_, message: Message):
    global AUTOEND_ENABLED
    usage = "<b>Example:</b>\n\n/autoend [enable|disable]"
    
    if len(message.command) != 2:
        return await message.reply_text(usage)
    
    state = message.text.split(None, 1)[1].strip().lower()
    
    if state == "enable":
        AUTOEND_ENABLED = True
        await autoend_on()
        await message.reply_text(
            "✅ Auto end stream enabled.\n\n"
            "Assistant will automatically leave the voice chat after 30 seconds "
            "when no one is listening."
        )
        # Start the checker if not already running
        if not hasattr(app, "autoend_task"):
            app.autoend_task = asyncio.create_task(auto_leave_checker())
            
    elif state == "disable":
        AUTOEND_ENABLED = False
        await autoend_off()
        await message.reply_text("❌ Auto end stream disabled.")
    else:
        await message.reply_text(usage)

# Start the checker when bot starts if autoend was enabled
@app.on_startup()
async def startup_autoend():
    try:
        # Check if autoend was enabled in database
        if await autoend_on() is True:
            global AUTOEND_ENABLED
            AUTOEND_ENABLED = True
            app.autoend_task = asyncio.create_task(auto_leave_checker())
    except Exception as e:
        print(f"Startup autoend error: {e}")
