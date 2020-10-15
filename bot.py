import asyncio

import discord
from discord.ext import commands
import pyttsx3


bot = commands.Bot(command_prefix='$')
FFMPEG_PATH = r'D:\Downloads\ffmpeg-4.3.1-2020-10-01-full_build\bin\ffmpeg.exe'


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def play(ctx, text):
    save_to_mp3(text, 'test.mp3')
    await play_mp3(ctx.author.voice.channel, 'test.mp3')


async def play_mp3(channel, mp3_path):
    """Plays an mp3 file in a voice channel"""
    vc = await channel.connect()

    vc.play(discord.FFmpegPCMAudio(source=mp3_path,
                                   executable=FFMPEG_PATH),
            after=lambda e: print('done', e))

    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()

    await vc.disconnect()


def save_to_mp3(text, filename):
    """Converts text to speech and saves as mp3"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.save_to_file(text, filename)
    engine.runAndWait()



bot.run('NzY2MTIwMzk0NjkyMjMxMTc5.X4evNw.DxRfS5qzcGNhy-LKXZYWfxdB06g')
