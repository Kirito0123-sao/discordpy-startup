import discord
import ast
import datetime
import re
import time
import asyncio
import random
import json
import os
from discord.ext import commands,tasks
import aiohttp
import youtube_dl
import ffmpeg


youtube_dl.utils.bug_reports_message = lambda: ''



bot = commands.Bot(command_prefix='kyon4545+')
token = os.environ['DISCORD_BOT_TOKEN']


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel=None):
        """Joins a voice channel"""

        if channel == None:
            channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))
        tip = randint(1, 10)
        if tip == 1:
            await ctx.send('**Tip:** Using the play command may offer better performance.')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')






@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def say(ctx, *, arg):
    await ctx.send(arg)   

    
@bot.command()
async def multiply(ctx, one: int, two: int):
    """ 掛け算 """
    await ctx.send(one * two)

@bot.command()
async def square(ctx, number: int):
    """ 二乗 """
    # `!multiply <number> <number>` と同じ
    await ctx.invoke(multiply, number, number)
    
    
@bot.command(pass_context=True) 
async def channel(ctx): 
    await bot.create_channel(ctx.message.server, 'test', type=discord.ChannelType.text)    
@bot.command(name="eval")
async def eval_(ctx, *, cmd):
    if ctx.author.id == 708720141193445470:
        try:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            env = {
                    'bot': ctx.bot,
                    'discord': discord,
                    'asyncio':asyncio,'random':random,'datetime':datetime,'re':re,
                    'commands': commands,'tasks':tasks,
                    'ctx': ctx,
                    '__import__': __import__
                }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            await eval(f"{fn_name}()", env)
            if ctx.message is not None:await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send([e])
            if ctx.message is not None:await ctx.message.add_reaction("❓")

@bot.command()
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)

@bot.command()
async def servericon(ctx):
    await ctx.send(ctx.guild.icon_url)    


@bot.command()
async def userinfo(ctx):
    user = ctx.message.author
    await ctx.send(
        "<@{0.id}> :useinfo\n"
        "ニックネーム: {0.display_name}\n"
        "ユーザー名: {0.name}\n"
        "Discriminator: {0.discriminator}\n"
        "ID: {0.id}\n".format(user))    
    

@bot.command()
async def quit(ctx):
    print(
        "[CRITICAL] {0.author} sent a command to shutdown the bot. Closing connection...".format(ctx))
    await ctx.send("I'm going to sleep :sleeping: see you soon! :blush:")
    await say_goodbye_to_status_channel()
    await bot.logout()
    
    
    
@bot.command()
async def join(ctx):
    print("Joining {0.author}'s channel...".format(ctx))


@bot.command()
async def leave(ctx):
    print("Leaving {0.author}'s channel...".format(ctx))


@bot.command()
async def play(ctx, args):
    print("Playing ??? on {0.author}'s channel...".format(ctx))    

    
@bot.listen()
async def on_ready():
    print("[INFO] Bot ready and connected to Discord")
    await set_now_playing("/help")
    await say_hello_to_status_channel()    
    
bot.run(token)
