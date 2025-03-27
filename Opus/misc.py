import socket
import time
import heroku3
from pyrogram import filters
import config
from Opus.core.mongo import mongodb
from .logging import LOGGER

SUDOERS = filters.user()
HEROKU_APP = None
_START_TIME = time.time()

HEROKU_URL_COMPONENTS = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "main",
]

def is_heroku():
    return "heroku" in socket.getfqdn()

def initialize_database():
    global db
    db = {}
    LOGGER(__name__).info("ᴅᴀᴛᴀʙᴀꜱᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ")

async def initialize_sudo_users():
    global SUDOERS
    

    SUDOERS.add(config.OWNER_ID)
    
    sudoers_db = mongodb.sudoers
    sudo_data = await sudoers_db.find_one({"sudo": "sudo"})
    sudo_users = [] if not sudo_data else sudo_data["sudoers"]
    
    if config.OWNER_ID not in sudo_users:
        sudo_users.append(config.OWNER_ID)
        await sudoers_db.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudo_users}},
            upsert=True,
        )
    
    for user_id in sudo_users:
        SUDOERS.add(user_id)
    
    LOGGER(__name__).info("ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ")

def initialize_heroku():
    global HEROKU_APP
    
    if not is_heroku():
        return
    
    if not all([config.HEROKU_API_KEY, config.HEROKU_APP_NAME]):
        LOGGER(__name__).warning(
            "ʜᴇʀᴏᴋᴜ ᴀᴘɪ ᴋᴇʏ ᴏʀ ᴀᴘᴘ ɴᴀᴍᴇ ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ. "
            "ᴘʟᴇᴀꜱᴇ ꜱᴇᴛ ʜᴇʀᴏᴋᴜ_ᴀᴘɪ_ᴋᴇʏ ᴀɴᴅ ʜᴇʀᴏᴋᴜ_ᴀᴘᴘ_ɴᴀᴍᴇ ɪɴ ᴄᴏɴꜰɪɢ."
            )
        return
    
    try:
        heroku_conn = heroku3.from_key(config.HEROKU_API_KEY)
        HEROKU_APP = heroku_conn.app(config.HEROKU_APP_NAME)
        LOGGER(__name__).info("ʜᴇʀᴏᴋᴜ ᴀᴘᴘ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴇꜱᴛᴀʙʟɪꜱʜᴇᴅ")
    except Exception as e:
        LOGGER(__name__).error(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ɪɴɪᴛɪᴀʟɪᴢᴇ ʜᴇʀᴏᴋᴜ ᴄᴏɴɴᴇᴄᴛɪᴏɴ: {str(e)}")
