import asyncio

import discord
from discord.ext import commands
import pyttsx3


class Audio(commands.Cog):
    def __init__(self, bot, ffmpeg_path):
        self.bot = bot
        self.ffmpeg_path = ffmpeg_path

    @commands.command()
    async def test(self, ctx, arg):
        await ctx.send(arg)

    @commands.command()
    async def play(self, ctx, text):
        self.save_to_mp3(text, 'test.mp3')
        await self.play_mp3(ctx.author.voice.channel, 'test.mp3')

    async def play_mp3(self, channel, mp3_path):
        """Plays an mp3 file in a voice channel"""
        vc = await channel.connect()

        vc.play(discord.FFmpegPCMAudio(source=mp3_path,
                                       executable=self.ffmpeg_path),
                after=lambda e: print('done', e))

        while vc.is_playing():
            await asyncio.sleep(1)
        vc.stop()

        await vc.disconnect()

    def save_to_mp3(self, text, filename):
        """Converts text to speech and saves as mp3"""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.save_to_file(text, filename)
        engine.runAndWait()