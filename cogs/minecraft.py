from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context

class Minecraft(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		
	@command(aliases=['mc', 'mcid', 'history', 'mcidhistory', 'mchistory'])
	async def minecraft(self, ctx: Context, *, args):
		pass

def setup(bot: Bot):
    bot.add_cog(Minecraft(bot))