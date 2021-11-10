from discord.ext.commands import Bot, Cog, Context, command
from discord_slash import cog_ext, SlashContext
import settings as s
from requests import delete
from os import getenv


class Admin(Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: Bot):
        self.bot = bot

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
