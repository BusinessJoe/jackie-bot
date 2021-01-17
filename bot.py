import os

from discord.ext import commands
from tts.ttsplayer import TTSPlayer


FFMPEG_PATH = os.environ['FFMPEG_PATH']


class JackieBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_cog(TTSPlayer(self, FFMPEG_PATH))

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


if __name__ == '__main__':
    bot = JackieBot(command_prefix='$')
    bot.run(os.getenv('DISCORD_TOKEN'))
