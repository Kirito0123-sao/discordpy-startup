from discord.ext import commands
import os
import traceback

import asyncio
import io
import textwrap
import contextlib
import json
import glob


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

    
    
@commands.command(name='eval', pass_context=True, description="※運営専用コマンド") # コマンド名:『eval』 省略コマンド:『なし』
    @commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, read_message_history=True) #これ絶対消しちゃダメ
    async def evals(self, ctx): #既に存在する関数名だったらERROR出るのでもし今後コマンドを追加するならコマンド名と同じ関数名にして下さい。(ここは例外)
        f"""
        evalコマンド。 基本的に何でもできる。
        試しに[{prefix}eval print("a")]って打ってみてほしい。
        そしたら大体どんな感じか理解できるはず！
        f"""
        try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
            if ctx.author.id not in admin_list:708720141193445470 # BOTの運営かどうかの判断
                return await ctx.send("指定ユーザーのみが使用できます")

            env = {'bot': self.bot, 'ctx': ctx, 'channel': ctx.channel, 'author': ctx.author, 'guild': ctx.guild, 'message': ctx.message, '_': self._last_result}
            env.update(globals())
            body = cleanup_code(ctx.message.content[6:].lstrip())
            stdout = io.StringIO()
            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
            try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            func = env['func']
            try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
                with contextlib.redirect_stdout(stdout):
                    ret = await func()
            except Exception as _:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
                    await ctx.message.add_reaction('\u2705')
                except Exception:
                    pass
                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```py\n{value}{ret}\n```')

        except (NotFound, asyncio.TimeoutError, Forbidden): # 編集した際に文字が見つからなかった, wait_forの時間制限を超過した場合, メッセージに接続できなかった
            return
        except: # 上のERROR以外のERROR出た場合はtracebackで表示するようにしています。 上手くコマンドが反応しない場合はコンソールを見てね！
            return print("エラー情報\n" + traceback.format_exc())

    @commands.command(name='all', pass_context=True, description="※運営専用コマンド") # コマンド名:『all』 省略コマンド:『なし』
    @commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, read_message_history=True) #これ絶対消しちゃダメ
    async def all(self, ctx, *, user_id:int): #既に存在する関数名だったらERROR出るのでもし今後コマンドを追加するならコマンド名と同じ関数名にして下さい。
        f"""
        ユーザーの全データを削除する
        {prefix}all ユーザーID でユーザーを指定する。
        f"""
        try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
            _, conn, cur = [sql for sql in self.bot.sqlite_list if ctx.author.id == sql[0]][0] # sqlite_listの中からデータベースに接続したというオブジェクトを取得
            if ctx.author.id not in admin_list: # BOTの運営かどうかの判断
                return await ctx.send("指定ユーザーのみが使用できます")

            msg = await ctx.send(content=f"<@{ctx.author.id}>これでいいの？\nこの変更で大丈夫な場合は『ok』\nキャンセルの場合は『no』と発言してください。", embed=Embed(description=f"{self.bot.get_user(user_id)}さんの全データを削除してもいいですか？"))
            # okかnoの発言を待つ処理。　もっと待つメッセージを絞る場合はlambdaにしてください。現在はokかnoだけしか認識できません。
            ok_no = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.lower() in ["ok", "no"])
            # await self.bot.wait_for('message')で返ってくるのは文字列型
            if ok_no.content.lower() == "ok":  # メッセージがokだった場合
                # 全てのテーブル名をを取得する
                await cur.execute('show tables')
                for user_deta in [str(t[0]) for t in await cur.fetchall()]:
                    # 取得したテーブルのcolumn全てを取得しそのcolumn名の中にuser_idというcolumnがある場合はデータ削除
                    await cur.execute(f"show columns from {user_deta};")
                    if "user_id" in str([c[0] for c in await cur.fetchall()]):
                        await cur.execute(f"DELETE FROM {user_deta} where user_id=?;", (user_id,))
                        await conn.commit() # データベースを最新の情報にするために更新する。 絶対必須
                return await msg.edit(embed=Embed(description=f"{self.bot.get_user(user_id)}さんの全データを削除しました！"))
            else: # メッセージがokではなくnoだった場合
                return await msg.edit(embed=Embed(description=f"{self.bot.get_user(user_id)}さんの全データを削除しませんでした！"))

        except (NotFound, asyncio.TimeoutError, Forbidden): # 編集した際に文字が見つからなかった, wait_forの時間制限を超過した場合, メッセージに接続できなかった
            return
        except: # 上のERROR以外のERROR出た場合はtracebackで表示するようにしています。 上手くコマンドが反応しない場合はコンソールを見てね！
            return print("エラー情報\n" + traceback.format_exc())    
    
 
bot.run(token)
