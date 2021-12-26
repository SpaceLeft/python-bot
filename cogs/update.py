from discord import Embed, Activity
from discord.ext.commands import Bot, Cog, command, Context
import settings as s
from datetime import datetime as d

class Update(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.log1 = '''Added Status command.
'''
		self.bot.log2 = '''Music commands.\n Hypixel stats commands.
'''
		self.bot.log3 = '''v1.0.2
'''
		self.bot.data['version'] = self.bot.log3[:-1]
	@command()
	async def update(self, ctx: Context):
		if ctx.author.id == 749013126866927713:
			await self.bot.change_presence(activity=Activity(name="{}help | {}".format(s.prefix, self.bot.data['version']), type=3))
			info = 'If you found a bug, please report with c.report or contact support.'
			embed = Embed(title='Updated the bot', description=self.bot.data['version'], colour=s.color1, timestamp=d.utcnow())
			embed.add_field(name='Changed', value=self.bot.log1[:-1], inline=False)
			embed.add_field(name='Coming soon...', value=self.bot.log2[:-1], inline=False)
			embed.set_footet(text=info)
			await self.bot.get_channel(885764049357381672).send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(Update(bot))