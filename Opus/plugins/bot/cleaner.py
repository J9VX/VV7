import asyncio
import os
import shutil
from pyrogram import filters
from Opus import app
from Opus.misc import SUDOERS

# Function to clean directories
async def clean_directories():
    while True:
        # List of directories to clean
        directories_to_clean = ["downloads", "cache"]
        
        for directory in directories_to_clean:
            try:
                if os.path.exists(directory):
                    shutil.rmtree(directory)  # Remove the directory and its contents
                    os.makedirs(directory)   # Recreate the directory
                    print(f"✅ Cleaned directory: {directory}")
                else:
                    print(f"⚠️ Directory does not exist: {directory}")
            except Exception as e:
                print(f"❌ Error cleaning directory {directory}: {e}")

        # Wait for 50 seconds before cleaning again
        await asyncio.sleep(80)

# Start the cleaner automatically when the bot starts (only for SUDOERS)
@app.on_message(filters.command("start_c") & filters.private & SUDOERS)
async def start_cleaner_on_boot(client, message):
    asyncio.create_task(clean_directories())
    await message.reply_text("🔄 ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ ᴘʟᴜɢɪɴ ꜱᴛᴀʀᴛᴇᴅ! ᴄʟᴇᴀɴɪɴɢ ᴇᴠᴇʀʏ 50 ꜱᴇᴄᴏɴᴅꜱ.")
    print("🔄 ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ ᴘʟᴜɢɪɴ ꜱᴛᴀʀᴛᴇᴅ! ᴄʟᴇᴀɴɪɴɢ ᴇᴠᴇʀʏ 50 ꜱᴇᴄᴏɴᴅꜱ.")

# Command to manually start the cleaner (optional)
@app.on_message(filters.command(["start_cleaner"]) & SUDOERS)
async def start_cleaner_manually(_, message):
    await message.reply_text(
        "<blockquote><b>🔄 ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ɪɴ ᴛʜᴇ ʙᴀᴄᴋɢʀᴏᴜɴᴅ. ɪᴛ ᴄʟᴇᴀɴꜱ ᴇᴠᴇʀʏ 50 ꜱᴇᴄᴏɴᴅꜱ.</b></blockquote>",
    )

# Command to stop the cleaner (optional, if you want to implement a stopping mechanism)
@app.on_message(filters.command(["stop_cleaner"]) & SUDOERS)
async def stop_cleaner(_, message):
    await message.reply_text(
        "<blockquote><b>🛑 ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ ᴄᴀɴɴᴏᴛ ʙᴇ ꜱᴛᴏᴘᴘᴇᴅ.</b></blockquote>",
    )


@app.on_message(filters.command("clear") & SUDOERS)
async def clear_terminal(_, message):
    # Clear the terminal immediately
    os.system('cls' if os.name == 'nt' else 'clear')
    await message.reply_text(
        "<blockquote><b>✅ ᴛᴇʀᴍɪɴᴀʟ ʟᴏɢꜱ ᴄʟᴇᴀʀᴇᴅ. ᴀᴜᴛᴏ ᴄʟᴇᴀʀɪɴɢ ᴇᴠᴇʀʏ 15 ꜱᴇᴄᴏɴᴅꜱ.</b></blockquote>",
    )

    while True:
        await asyncio.sleep(15)  # Wait for 5 seconds
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 Terminal logs cleared automatically.")
