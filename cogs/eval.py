import discord, asyncio, youtube_dl, random, time, datetime
from discord.ext.commands import Bot, Cog, command, Context, CommandError
from functools import partial
from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT as pycf
from subprocess import run, PIPE

async_compile = partial(compile, mode="exec", filename="<discord>", flags=pycf)


def async_eval(src, variables=None):
    if not variables:
        variables = {}
    # XXX: コルーチンにするには、最低限一つの await を含む必要が有る為
    # コンパイル対象のコードの末尾に await asyncio.sleep(0) を追加してます。
    # ここは、他により良い解決策があるかもしれません。
    return eval(async_compile('{}\nawait asyncio.sleep(0)'.format(src)), globals(), variables)


class Developer(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def eval(self, ctx: Context, types : str, *, arg: str):
        if ctx.author.id == 897030094290321468 or ctx.author.id == 749013126866927713:
            args = {"imp": __import__, "client": self.bot, "self": self.bot, "bot": self.bot, "ctx": ctx}
            if arg.find('```') != -1:
                if arg.find('```python') != -1:
                    arg = arg.split('```python')[1].split('```')[0]
                elif arg.find('```py') != -1:
                    arg = arg.split('```py')[1].split('```')[0]
                elif arg.find('```') != -1:
                    arg = arg.split('```')[1].split('```')[0]
            try:
                if types == 'a':
                    result = await async_eval(arg, args)
                elif types == 'b':
                    result = run('python -c \"{}\"'.format(';'.join(arg.split('\n'))), stdout=PIPE, stderr=PIPE, shell=True)
                    if not result.stderr:
                        result = result.stdout
                    else:
                        raise CommandError('Error : {}'.format(result.stderr))
                else:
                    result = eval(arg)
                if result is not None:
                    if type(result) == bytes:
                        result = result.decode()
                    await ctx.send(f'```python\n{result}\n```')
            except Exception as e:
                raise CommandError('Error : {}'.format(e))


def setup(bot: Bot):
    bot.add_cog(Developer(bot))
