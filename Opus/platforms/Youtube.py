import asyncio
import glob
import json
import logging
import os
import random
import re
from typing import Union, Optional, Tuple, List, Dict

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from Opus.utils.database import is_on_off
from Opus.utils.formatters import time_to_seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _get_cookie_file(self) -> Optional[str]:
        """Selects a random cookie file from the cookies directory."""
        try:
            cookie_dir = os.path.join(os.getcwd(), "cookies")
            os.makedirs(cookie_dir, exist_ok=True)
            
            txt_files = glob.glob(os.path.join(cookie_dir, "*.txt"))
            if not txt_files:
                logger.warning("No cookie files found in the cookies directory.")
                return None

            chosen_file = random.choice(txt_files)
            log_file = os.path.join(cookie_dir, "logs.csv")
            
            with open(log_file, "a") as f:
                f.write(f"Selected cookie file: {chosen_file}\n")
            
            return chosen_file
        except Exception as e:
            logger.error(f"Error selecting cookie file: {e}")
            return None

    async def _run_shell_cmd(self, cmd: str) -> str:
        """Runs a shell command and returns its output."""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8").strip()
            if "unavailable videos are hidden" in error_msg.lower():
                return stdout.decode("utf-8").strip()
            logger.error(f"Command failed: {cmd}\nError: {error_msg}")
            return error_msg
        return stdout.decode("utf-8").strip()

    async def _get_video_info(self, link: str) -> Optional[Dict]:
        """Fetches video info using yt-dlp."""
        cookie_file = self._get_cookie_file()
        cmd = [
            "yt-dlp",
            "--cookies", cookie_file if cookie_file else "",
            "-J",
            link,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            logger.error(f"Failed to fetch video info: {stderr.decode()}")
            return None
        
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            logger.error("Failed to parse video info.")
            return None

    async def check_file_size(self, link: str) -> Optional[int]:
        """Returns the file size in bytes if available."""
        info = await self._get_video_info(link)
        if not info:
            return None
        
        formats = info.get("formats", [])
        total_size = sum(f.get("filesize", 0) for f in formats)
        return total_size if total_size > 0 else None

    async def exists(self, link: str, videoid: bool = False) -> bool:
        """Checks if the given link is a valid YouTube URL."""
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Optional[str]:
        """Extracts a YouTube URL from a Pyrogram message."""
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        
        for msg in messages:
            # Check entities (URLs)
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[entity.offset : entity.offset + entity.length]
            
            # Check caption entities (TEXT_LINK)
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        
        return None

    async def details(
        self, 
        link: str, 
        videoid: bool = False
    ) -> Tuple[str, str, int, str, str]:
        """Fetches video details (title, duration, thumbnail, ID)."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        results = VideosSearch(link, limit=1)
        video_data = (await results.next())["result"][0]
        
        title = video_data["title"]
        duration_min = video_data["duration"]
        thumbnail = video_data["thumbnails"][0]["url"].split("?")[0]
        vidid = video_data["id"]
        duration_sec = 0 if duration_min == "None" else time_to_seconds(duration_min)
        
        return title, duration_min, duration_sec, thumbnail, vidid

    async def video(self, link: str, videoid: bool = False) -> Tuple[int, str]:
        """Fetches the direct video URL (best quality up to 720p)."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = self._get_cookie_file()
        cmd = [
            "yt-dlp",
            "--cookies", cookie_file if cookie_file else "",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        
        if stdout:
            return (1, stdout.decode().split("\n")[0])
        return (0, stderr.decode())

    async def download(
        self,
        link: str,
        mystic,
        video: bool = False,
        videoid: bool = False,
        songaudio: bool = False,
        songvideo: bool = False,
        format_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Union[Tuple[str, bool], None]:
        """Downloads a video/audio file from YouTube."""
        if videoid:
            link = self.base + link
        
        loop = asyncio.get_running_loop()
        cookie_file = self._get_cookie_file()
        
        # Check file size if downloading directly
        if video and not await is_on_off(1):
            file_size = await self.check_file_size(link)
            if file_size and (file_size / (1024 * 1024)) > 250:  # 250MB limit
                await mystic.edit("File size exceeds 250MB limit.")
                return None
        
        def _download_audio():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(filepath):
                    ydl.download([link])
                return filepath

        def _download_video():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(filepath):
                    ydl.download([link])
                return filepath

        if songvideo and format_id and title:
            await loop.run_in_executor(None, _download_video)
            return f"downloads/{title}.mp4", True
        
        elif songaudio and format_id and title:
            await loop.run_in_executor(None, _download_audio)
            return f"downloads/{title}.mp3", True
        
        elif video:
            if await is_on_off(1):
                filepath = await loop.run_in_executor(None, _download_video)
                return filepath, True
            else:
                status, url = await self.video(link, videoid)
                return (url, False) if status else (None, False)
        
        else:  # Audio-only download
            filepath = await loop.run_in_executor(None, _download_audio)
            return filepath, True
