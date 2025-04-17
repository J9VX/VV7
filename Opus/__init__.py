from Opus.core.bot import Anony
from Opus.core.dir import dirr
from Opus.core.git import git
from Opus.core.userbot import Userbot
from Opus.misc import dbb, heroku
import asyncio

from .logging import LOGGER

dirr()
asyncio.run(git())
dbb()
heroku()

app = Anony()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
