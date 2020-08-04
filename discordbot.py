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



bot = commands.Bot(command_prefix='kyon4545+')
token = os.environ['DISCORD_BOT_TOKEN']


bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed (title="Enjoy Python", description="kyon4545<:masscheart:740169772615860253>", color=0xeee657)
    embed.add_field (name="prefix", value="kyon4545+", inline=False)
    embed.add_field (name="kyon4545+help", value="コマンドのヘルプ", inline=False)
    embed.add_field (name="avatar", value="ユーザーのアイコンを見ます", inline=False)
    embed.add_field (name="servericon", value="サーバーのアイコンを見ます", inline=False)
    embed.add_field (name="say", value="say", inline=False)
    await ctx.send (embed=embed)



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
    
    
    
@bot.command(pass_context=True)
async def join(ctx):
    await bot.join_voice_channel(bot.get_channel('739143904347160587'))


@bot.command(pass_context=True)
async def leave(ctx):
    voice_client = bot.voice_client_in(ctx.message.server)
    await voice_client.disconnect()



@bot.command()
async def play(ctx, args):
    print("Playing ??? on {0.author}'s channel...".format(ctx))    

    
@bot.listen()
async def on_ready():
    print("[INFO] Bot ready and connected to Discord")
    await set_now_playing("/help")
    await say_hello_to_status_channel()    

    
@bot.event
async def on_member_join(member):
    channel = discord.utils.get (member.guild.text_channels, name='入室ログ')
    server=member.guild
    e=discord.Embed (description="サーバー入室ログ")
    e.add_field (name="参加ありがとうございます:", value=f"{member.mention}", inline=False)
    await channel.send (embed=e)    

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        await ctx.send(f"コマンドは存在しません")

bot.run(token)
