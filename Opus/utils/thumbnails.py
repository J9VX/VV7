import asyncio
from io import BytesIO

import httpx
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from aiofiles.os import path as aiopath

import config
#from src.logger import LOGGER
from Opus.logging import LOGGER
from Cache.dataclass import CachedTrack

FONTS = {
    "cfont": ImageFont.truetype("src/utils/cfont.ttf", 15),
    "dfont": ImageFont.truetype("src/utils/font2.otf", 12),
    "nfont": ImageFont.truetype("src/utils/font.ttf", 10),
    "tfont": ImageFont.truetype("src/utils/font.ttf", 20),
}


def resize_thumbnail(img: Image.Image, target_width: int = 1280, target_height: int = 720) -> Image.Image:
    """
    Resize and crop thumbnail to fill landscape dimensions without black bars.
    Maintains aspect ratio while filling the entire space.
    """
    # Calculate aspect ratios
    target_ratio = target_width / target_height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider than target - scale to match height then crop sides
        new_height = target_height
        new_width = int(img.width * (new_height / img.height))
    else:
        # Image is taller than target - scale to match width then crop top/bottom
        new_width = target_width
        new_height = int(img.height * (new_width / img.width))

    # Resize with high-quality filter
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate crop coordinates
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2

    return img.crop((left, top, right, bottom))


async def fetch_image(url: str) -> Image.Image | None:
    if not url:
        return None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            return resize_thumbnail(img)
        except Exception as e:
            LOGGER.error(f"Image loading error: {e}")
            return None


def clean_text(text: str, limit: int = 17) -> str:
    """Sanitizes and truncates text to fit within the limit."""
    text = text.strip()[:limit]
    return f"{text}..." if len(text) == limit else text


def add_controls(img: Image.Image) -> Image.Image:
    """Adds blurred background effect and overlay controls."""
    # Create a blurred version of the image
    blurred = img.filter(ImageFilter.GaussianBlur(25))
    
    # Create a semi-transparent overlay
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 128))
    
    # Combine the blurred image with overlay
    bg = Image.alpha_composite(blurred, overlay)
    
    # Add controls image centered at the bottom
    controls = Image.open("src/utils/controls.png").convert("RGBA")
    controls_width, controls_height = controls.size
    x_pos = (img.width - controls_width) // 2
    y_pos = img.height - controls_height - 20  # 20px from bottom
    
    bg.paste(controls, (x_pos, y_pos), controls)
    
    return bg


def make_sq(image: Image.Image, size: int = 200) -> Image.Image:
    """Crops an image into a rounded square."""
    width, height = image.size
    side_length = min(width, height)
    crop = image.crop(
        (
            (width - side_length) // 2,
            (height - side_length) // 2,
            (width + side_length) // 2,
            (height + side_length) // 2,
        )
    )
    resize = crop.resize((size, size), Image.Resampling.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=30, fill=255)

    rounded = ImageOps.fit(resize, (size, size))
    rounded.putalpha(mask)
    return rounded


def get_duration(duration: int, time: str = "0:24") -> str:
    """Calculates remaining duration."""
    try:
        m1, s1 = divmod(duration, 60)
        m2, s2 = map(int, time.split(":"))
        sec = (m1 * 60 + s1) - (m2 * 60 + s2)
        _min, sec = divmod(sec, 60)
        return f"{_min}:{sec:02d}"
    except Exception as e:
        LOGGER.error(f"Duration calculation error: {e}")
        return "0:00"


async def get_thumb(song: CachedTrack) -> str:
    """Generates and saves a thumbnail for the song."""
    save_dir = f"database/photos/{song.track_id}.png"
    if await aiopath.exists(save_dir):
        return save_dir

    title, artist = clean_text(song.name), clean_text(song.artist or "Spotify")
    duration = song.duration or 0

    thumb = await fetch_image(song.thumbnail)
    if not thumb:
        return config.YOUTUBE_IMG_URL

    # Process Image
    bg = add_controls(thumb)
    image = make_sq(thumb)

    # Positions (centered horizontally, slightly above controls)
    paste_x = (bg.width - image.width) // 2
    paste_y = 100  # 100px from top
    bg.paste(image, (paste_x, paste_y), image)

    draw = ImageDraw.Draw(bg)
    
    # Text positions (centered)
    text_x = bg.width // 2
    
    # "Fallen Beatz" text (small, centered)
    fallen_text = "VX"
    fallen_width = draw.textlength(fallen_text, font=FONTS["nfont"])
    draw.text((text_x - fallen_width//2, paste_y + image.height + 20), 
              fallen_text, (192, 192, 192), font=FONTS["nfont"])
    
    # Song title (larger, centered)
    title_width = draw.textlength(title, font=FONTS["tfont"])
    draw.text((text_x - title_width//2, paste_y + image.height + 40), 
              title, (255, 255, 255), font=FONTS["tfont"])
    
    # Artist name (medium, centered)
    artist_width = draw.textlength(artist, font=FONTS["cfont"])
    draw.text((text_x - artist_width//2, paste_y + image.height + 70), 
              artist, (255, 255, 255), font=FONTS["cfont"])
    
    # Duration (bottom right)
    duration_text = get_duration(duration)
    duration_width = draw.textlength(duration_text, font=FONTS["dfont"])
    draw.text((bg.width - duration_width - 30, bg.height - 50), 
              duration_text, (192, 192, 192), font=FONTS["dfont"])

    await asyncio.to_thread(bg.save, save_dir)
    return save_dir if await aiopath.exists(save_dir) else config.YOUTUBE_IMG_URL
