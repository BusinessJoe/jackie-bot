import os

from discord.ext import commands
from tts.ttsplayer import TTSPlayer

FFMPEG_PATH = r'D:\Downloads\ffmpeg-4.3.1-2020-10-01-full_build\bin\ffmpeg.exe'


class JackieBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_cog(TTSPlayer(self, FFMPEG_PATH))

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


if __name__ == '__main__':
    bot = JackieBot(command_prefix='$')
    bot.run(os.getenv('DISCORD_TOKEN'))
