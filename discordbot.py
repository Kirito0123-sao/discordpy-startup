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

 @commands.command()
    async def maru(self, ctx, *, member: discord.Member = None):
        """アバターを丸にする"""

        # ユーザーが指定されていなかった場合、メッセージを送信したユーザーを使用します。
        member = member or ctx.author

        # 処理をしながら「入力中」を表示する
        async with ctx.typing():
            if isinstance(member, discord.Member):
                # サーバーにいるならユーザーの表示色を取得する
                member_colour = member.colour.to_rgb()
            else:
                # DMなどにいるなら(0, 0, 0)を使用する
                member_colour = (0, 0, 0)

            # アバターデータを bytes として取得。
            avatar_bytes = await self.get_avatar(member)

            # partialオブジェクトを作る
            # fnが呼び出されると、avatar_bytesとmember_colorを引数として渡してself.processingを実行するのと同様の動作をします。
            fn = partial(self.processing, avatar_bytes, member_colour)

            # executorを使ってfnを別スレッドで実行します。
            # こうやって非同期的に関数が返すまで待つことができます
            # final_bufferはself.processingが返すバイトストリームになります。
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            # ファイル名「maru.png」の指定とfinal_bufferの内部でファイルを準備して
            file = discord.File(filename="maru.png", fp=final_buffer)

            # 最後にファイルをアップします。
            await ctx.send(file=file)


def setup(bot: commands.Bot):

bot.run(token)
