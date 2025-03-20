import asyncio
import os
import shutil
from Opus import app

GROUP_CHAT_ID = -1002064111110 

async def clean_directories():
    while True:
        directories_to_clean = ["downloads", "raw_files", "cache"]
        
        for directory in directories_to_clean:
            try:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                    os.makedirs(directory)
                    await app.send_message(
                        GROUP_CHAT_ID,
                        f"✅ **ᴄʟᴇᴀɴᴇᴅ ᴅɪʀᴇᴄᴛᴏʀʏ:** `{directory}`"
                    )
                else:
                    await app.send_message(
                        GROUP_CHAT_ID,
                        f"⚠️ **ᴅɪʀᴇᴄᴛᴏʀʏ ᴅᴏᴇꜱ ɴᴏᴛ ᴇxɪꜱᴛ:** `{directory}`"
                    )
            except Exception as e:
                await app.send_message(
                    GROUP_CHAT_ID,
                    f"❌ **ᴇʀʀᴏʀ ᴄʟᴇᴀɴɪɴɢ ᴅɪʀᴇᴄᴛᴏʀʏ** `{directory}`: `{e}`"
                )

        # Wait for 50 seconds before cleaning again
        await asyncio.sleep(50)

# Start the cleaner automatically when the bot starts
@app.on_startup()
async def start_cleaner_on_boot():
    asyncio.create_task(clean_directories())
    await app.send_message(
        GROUP_CHAT_ID,
        "🔄 **ᴘᴀꜱꜱɪᴠᴇ ᴄʟᴇᴀɴᴇʀ ᴘʟᴜɢɪɴ ꜱᴛᴀʀᴛᴇᴅ!** ᴄʟᴇᴀɴɪɴɢ ᴇᴠᴇʀʏ 50 ꜱᴇᴄᴏɴᴅꜱ."
    )
