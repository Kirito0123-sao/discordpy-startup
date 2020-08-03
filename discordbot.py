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
async def ping(ctx):
    await ctx.send(ctx.🏓 Pong! {round(bot.latency*1000)}ms")    
    
bot.run(token)
