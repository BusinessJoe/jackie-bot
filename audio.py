import asyncio

import discord
from discord.ext import commands
import pyttsx3


class Audio(commands.Cog):
    def __init__(self, bot, ffmpeg_path):
        self.bot = bot
        self.ffmpeg_path = ffmpeg_path

        self.author = None
        self.text_channel = None
        self.voice_channel = None
        self.vc = None

    async def connect(self):
        self.vc = await self.voice_channel.connect()

    async def disconnect(self):
        """Disconnects from vc and resets binding variables"""
        await self.vc.disconnect()

        self.author = None
        self.text_channel = None
        self.voice_channel = None
        self.vc = None

    @commands.Cog.listener()
    async def on_message(self, m):
        if m.content.startswith(self.bot.command_prefix):  # Ignore commands
            return

        if self.vc and \
                m.author == self.author and \
                m.channel == self.text_channel:
            await self.play(self.voice_channel, m.content)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Disconnect automatically when bound user leaves"""
        if member != self.author:
            return

        if after.channel is None:
            await self.disconnect()

    @commands.command()
    async def bind(self, ctx):
        self.author = ctx.author
        self.text_channel = ctx.message.channel
        self.voice_channel = self.author.voice.channel

        await self.connect()

    @commands.command()
    async def unbind(self, ctx):
        await self.disconnect()

    @commands.command()
    async def play(self, voice_channel, text):
        self.save_to_mp3(text, 'test.mp3')
        await self.play_mp3(voice_channel, 'test.mp3')

    async def play_mp3(self, channel, mp3_path):
        """Plays an mp3 file in a voice channel"""
        self.vc.play(discord.FFmpegPCMAudio(source=mp3_path,
                                            executable=self.ffmpeg_path),
                     after=lambda e: print('done', e))

        while self.vc.is_playing():
            await asyncio.sleep(1)
        self.vc.stop()

    def save_to_mp3(self, text, filename):
        """Converts text to speech and saves as mp3"""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.save_to_file(text, filename)
        engine.runAndWait()
