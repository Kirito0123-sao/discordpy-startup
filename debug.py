 @commands.command(name='eval', pass_context=True, description="※運営専用コマンド") # コマンド名:『eval』 省略コマンド:『なし』
    @commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, read_message_history=True) #これ絶対消しちゃダメ
    async def evals(self, ctx): #既に存在する関数名だったらERROR出るのでもし今後コマンドを追加するならコマンド名と同じ関数名にして下さい。(ここは例外)
        f"""
        evalコマンド。 基本的に何でもできる。
        試しに[{prefix}eval print("a")]って打ってみてほしい。
        そしたら大体どんな感じか理解できるはず！
        f"""
        try: # ERRORが起きるか起きないか。起きたらexceptに飛ばされる
            if ctx.author.id not in admin_list: # BOTの運営かどうかの判断
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
