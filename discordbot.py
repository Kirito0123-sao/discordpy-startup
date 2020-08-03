from discord.ext import commands
import os
import traceback

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
async def say(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def test(ctx, *, arg):
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
    
 
bot.run(token)
