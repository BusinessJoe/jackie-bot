import asyncio

import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='$')
FFMPEG_PATH = r'D:\Downloads\ffmpeg-4.3.1-2020-10-01-full_build\bin\ffmpeg.exe'


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def play(ctx):
    channel = ctx.author.voice.channel
    vc = await channel.connect()

    vc.play(discord.FFmpegPCMAudio(source='file_example_MP3_700KB.mp3',
                                   executable=FFMPEG_PATH),
            after=lambda e: print('done', e))

    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()

    await vc.disconnect()


bot.run('NzY2MTIwMzk0NjkyMjMxMTc5.X4evNw.DxRfS5qzcGNhy-LKXZYWfxdB06g')
