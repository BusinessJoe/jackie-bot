from typing import Dict, List
import asyncio
import os

import discord
from discord.ext import commands
import pyttsx3
from tts.ttssettings import TTSSettings


class TTSPlayer(commands.Cog):
    def __init__(self, bot, ffmpeg_path):
        self.bot = bot
        self.settings = TTSSettings()
        self.ffmpeg_path = ffmpeg_path

        self.author: Dict = {}
        self.text_channel: Dict = {}
        self.vc: Dict = {}

        self.message_queue: Dict[List[str]] = {}

    async def connect(self, channel):
        guild_id = channel.guild.id

        self.message_queue[guild_id] = []

        if self.vc.get(guild_id) is None:
            print(f'Connecting to {channel}')
            self.vc[guild_id] = await channel.connect()
        else:
            if self.vc[guild_id].channel != channel:
                await self.vc[guild_id].disconnect()
                print(f'Connecting to {channel}')
                self.vc[guild_id] = await channel.connect()

    async def disconnect(self, guild_id):
        """Disconnects from vc and clears message queue"""
        print(f'Disconnecting from {self.vc[guild_id].channel}')
        await self.vc[guild_id].disconnect()
        del self.vc[guild_id]
        del self.message_queue[guild_id]

    @commands.Cog.listener()
    async def on_message(self, m):
        if m.content.startswith(self.bot.command_prefix):  # Ignore commands
            return

        guild_id = m.guild.id
        if self.vc.get(guild_id) and \
                m.author == self.author[guild_id] and \
                m.channel == self.text_channel[guild_id]:
            self.message_queue[guild_id].append(m.content)

            if not self.vc[guild_id].is_playing():
                await self.play_queue(guild_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Disconnect automatically when bound user leaves"""
        guild_id = (before.channel or after.channel).guild.id

        if member != self.author.get(guild_id):
            return

        # Ignore changes that keep the member in the same channel
        if before.channel == after.channel:
            return

        if after.channel is not None:
            await self.connect(after.channel)
        else:
            await self.disconnect(guild_id)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def bind(self, ctx):
        guild_id = ctx.guild.id
        self.author[guild_id] = ctx.author
        self.text_channel[guild_id] = ctx.message.channel

        if self.author[guild_id].voice is not None:
            await self.connect(self.author[guild_id].voice.channel)

        await ctx.send(f'Now listening to {ctx.author}')

        if not self.settings.user_exists(self.author[guild_id].id):
            self.settings.create_user(self.author[guild_id].id)
        print(f'Bound to {ctx.author}')

    @commands.command()
    async def unbind(self, ctx):
        """Disconnects from vc and resets binding variables"""
        guild_id = ctx.guild.id
        await self.disconnect(guild_id)

        del self.author[guild_id]
        del self.text_channel[guild_id]

        await ctx.send(f'No longer listening to {ctx.author}')

    @commands.command(name='rate')
    async def set_rate(self, ctx, value: int):
        self.settings.update_user(ctx.author.id, rate=value)

    @commands.command(name='voice')
    async def set_voice_id(self, ctx, value: int):
        self.settings.update_user(ctx.author.id, voice_id=value)

    @commands.command(name='volume')
    async def set_volume(self, ctx, value: float):
        self.settings.update_user(ctx.author.id, volume=value / 100)

    @commands.command(name='defaults')
    async def set_defaults(self, ctx):
        self.settings.delete_user(ctx.author.id)
        self.settings.create_user(ctx.author.id)

    async def play(self, text, guild_id):
        filename = f'messages/{guild_id}.mp3'
        self.save_to_mp3(text, filename, guild_id)
        await self.play_mp3(filename, guild_id)
        self.delete_file(filename)

    async def play_queue(self, guild_id):
        queue = self.message_queue[guild_id]
        while queue:
            message = queue.pop(0)
            print(f"Saying '{message}' in guild {guild_id}")
            await self.play(message, guild_id)

    async def play_mp3(self, mp3_path, guild_id):
        """Plays an mp3 file in a voice channel"""
        self.vc[guild_id].play(discord.FFmpegPCMAudio(source=mp3_path,
                                                      executable=self.ffmpeg_path,
                                                      before_options='-guess_layout_max 0'))

        while self.vc[guild_id].is_playing():
            await asyncio.sleep(1)
        self.vc[guild_id].stop()

    def save_to_mp3(self, text, filename, guild_id):
        """Converts text to speech and saves as mp3"""
        user_settings = self.settings.get_user_settings(self.author[guild_id].id)

        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', user_settings['rate'])
        engine.setProperty('voice', voices[user_settings['voice_id']].id)
        engine.setProperty('volume', user_settings['volume'])
        engine.save_to_file(text, filename)
        engine.runAndWait()

    def delete_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
