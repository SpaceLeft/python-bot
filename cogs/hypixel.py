from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context
import requests


class Hypixel(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		
	@command(aliases=[])
	async def example(self, ctx: Context, *, args):
		a = requests.get('https://api.hypixel.net/key?key=7b0c4dde-f495-4f9c-b7cf-cd2cb6b75263').json()
		print(a)

def setup(bot: Bot):
    bot.add_cog(Hypixel(bot))