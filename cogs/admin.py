import discord, asyncio, youtube_dl, random, time, datetime
from discord.ext.commands import Bot, Cog, command, Context, CommandError
from functools import partial
from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT as pycf
from subprocess import run, PIPE
from discord.ext.commands import Bot, Cog, Context, command
from discord_slash import cog_ext, SlashContext
import settings as s
from requests import delete
from os import getenv

class Admin(Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.async_compile = partial(compile, mode="exec", filename="<discord>", flags=pycf)]

    def async_eval(src, variables=None):
        if not variables:
            variables = {}
        return eval(self.async_compile('{}\nawait asyncio.sleep(0)'.format(src)), globals(), variables)

    @command()
    async def eval(self, ctx: Context, types : str, *, arg: str):
        if ctx.author.id == 897030094290321468 or ctx.author.id == 749013126866927713:
            args = {"import":  __import__, "client": self.bot, "self": self.bot, "bot": self.bot, "ctx": ctx}
            if arg.find('```') != -1:
                if arg.find('```python') != -1:
                    arg = arg.split('```python')[1].split('```')[0]
                elif arg.find('```py') != -1:
                    arg = arg.split('```py')[1].split('```')[0]
                elif arg.find('```') != -1:
                    arg = arg.split('```')[1].split('```')[0]
            try:
                if types == 'a':
                    result = await self.async_eval(arg, args)
                elif types == 'b':
                    open('{}.py'.format(ctx.author.id), 'w').write(arg)
                    result = run('python {}.py'.format(ctx.author.id), stdout=PIPE, stderr=PIPE, shell=True)
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

    @command(name="restart")
    async def restart(self, ctx: Context):
        delete('https://api.heroku.com/apps/akishoudayo-bot/dynos', headers={"Accept": "application/vnd.heroku+json; version=3", "Authorization": "Bearer {}".format(getenv('API_KEY'))})
        await ctx.send('Successfully Restarted')

    @cog_ext.cog_slash(name="load", guild_ids=s.guild)
    async def _load(self, ctx: SlashContext, cog: str):
        try:
            self.bot.reload_extension("cogs." + cog)
            await ctx.send(content=f"Loaded Extension: {cog}.py")
        except Exception as e:
            self.bot.log(4, e)
            await ctx.send(content=f"Failed to Load Extension: {cog}.py")

    @cog_ext.cog_slash(name="unload", guild_ids=s.guild)
    async def _unload(self, ctx: SlashContext, cog: str):
        try:
            self.bot.reload_extension("cogs." + cog)
            await ctx.send(content=f"Unloaded Extension: {cog}.py")
        except Exception as e:
            self.bot.log(4, e)
            await ctx.send(content=f"Failed to Unpoad Extension: {cog}.py")

    @cog_ext.cog_slash(name="reload", guild_ids=s.guild)
    async def _reload(self, ctx: SlashContext, cog: str):
        try:
            self.bot.reload_extension("cogs." + cog)
            await ctx.send(content=f"Reloaded Extension: {cog}.py")
        except Exception as e:
            self.bot.log(4, e)
            await ctx.send(content=f"Failed to Reload Extension: {cog}.py")

    async def cog_check(self, ctx: Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.author.id == 897030094290321468 or ctx.author.id == 749013126866927713:
            return True
        await ctx.reply("You cannot run this command.")
        return False

    @command(name="load")
    async def load_cog(self, ctx: Context, *, cog: str = None):
        try:
            self.bot.load_extension("cogs." + cog)
            await ctx.reply(f"Loaded Extension: {cog}.py", mention_author=False)
        except Exception as e:
            self.bot.log(4, e)
            await ctx.reply(f"Failed to Load Extension: {cog}.py", mention_author=False)

    @command(name="unload")
    async def unload_cog(self, ctx: Context, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
            await ctx.reply(f"Unloaded Extension: {cog}.py", mention_author=False)
        except Exception as e:
            self.bot.log(4, e)
            await ctx.reply(f"Failed to Unload Extension: {cog}.py", mention_author=False)

    @command(name="reload")
    async def reload_cog(self, ctx: Context, *, cog: str):
        try:
            self.bot.reload_extension("cogs." + cog)
            await ctx.reply(f"Reloaded Extension: {cog}.py", mention_author=False)
        except Exception as e:
            self.bot.log(4, e)
            await ctx.reply(f"Failed to Reload Extension: {cog}.py", mention_author=False)


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
