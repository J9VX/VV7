import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from typing import Dict

class BrutalAutoEnd:
    def __init__(self, bot: Client):
        self.bot = bot
        self.modes: Dict[int, str] = {}  # chat_id: mode
        self.semaphore = asyncio.Semaphore(5)
        
        # Add handlers
        self.bot.add_handler(
            filters.command("autoend") & filters.user("SUDOERS"),
            self.autoend_handler
        )
        
        # Start killer loop
        asyncio.create_task(self.killer_loop())

    async def autoend_handler(self, client: Client, message: Message):
        """Handle autoend commands with brutal efficiency"""
        if len(message.command) < 2:
            return await message.reply("⚡ Usage: /autoend [on|1min|instant|off|nukeall]")

        cmd = message.command[1].lower()
        chat_id = message.chat.id

        if cmd == "on":
            self.modes[chat_id] = "normal"
            await message.reply("⚡ Autoend: 3min timeout")
            
        elif cmd == "1min":
            self.modes[chat_id] = "aggressive"
            await message.reply("💢 Autoend: 1min timeout")
            
        elif cmd == "instant":
            self.modes[chat_id] = "instant"
            await self.nuke_call(chat_id)
            await message.reply("☢️ Brutal mode: Instant kill active")
            
        elif cmd == "off":
            self.modes.pop(chat_id, None)
            await message.reply("⚡ Autoend disabled")
            
        elif cmd == "nukeall":
            await self.mass_nuke()
            await message.reply("💥 NUKE COMPLETE: All calls terminated")
            
        else:
            await message.reply("⚡ Invalid command")

    async def nuke_call(self, chat_id: int):
        """Terminate call with extreme prejudice"""
        async with self.semaphore:
            try:
                await self.bot.leave_group_call(chat_id)
                print(f"☠️ Brutal kill: {chat_id}")
            except Exception as e:
                print(f"💣 Kill failed: {chat_id} - {str(e)}")

    async def should_nuke(self, chat_id: int) -> bool:
        """Determine if a call should be terminated"""
        mode = self.modes.get(chat_id)
        if not mode or mode == "off":
            return False
            
        try:
            participants = await self.bot.get_group_call_participants(chat_id)
            if len(participants) > 1:  # Others present
                return False
                
            if mode == "instant":
                return True
                
            call = await self.bot.get_group_call(chat_id)
            if call:
                elapsed = (datetime.now() - call.start_date).seconds
                threshold = 180 if mode == "normal" else 60
                return elapsed > threshold
                
        except Exception as e:
            print(f"🔥 Check failed: {chat_id} - {str(e)}")
            return False

    async def killer_loop(self):
        """Continuous execution loop"""
        while True:
            try:
                await self.check_all_chats()
            except Exception as e:
                print(f"💀 Killer loop crashed: {str(e)}")
            await asyncio.sleep(30)  # Check every 30 seconds

    async def check_all_chats(self):
        """Check all active chats"""
        active_chats = await self.get_active_chats()  # Implement your chat cache
        tasks = [self.check_chat(cid) for cid in active_chats]
        await asyncio.gather(*tasks)

    async def check_chat(self, chat_id: int):
        """Check and nuke a single chat"""
        if await self.should_nuke(chat_id):
            await self.nuke_call(chat_id)

    async def mass_nuke(self):
        """Terminate all active calls"""
        active_chats = await self.get_active_chats()
        await asyncio.gather(*[self.nuke_call(cid) for cid in active_chats])

    async def get_active_chats(self):
        """Replace with your actual chat cache implementation"""
        return []  # Return list of active chat IDs


# Usage:
# bot = Client(...)
# autoend = BrutalAutoEnd(bot)
# bot.run()
