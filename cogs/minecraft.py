from discord import Embed, File
from requests import get
from base64 import b64decode
from discord.ext.commands import Bot, Cog, command, Context

class Minecraft(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		
	@command(aliases=['mc', 'mcid', 'history', 'mcidhistory', 'mchistory'])
	async def minecraft(self, ctx: Context, *, args):
		pass

	@command(aliases=['check', 'servercheck', 'ch'])
	async def mccheck(self, ctx: Context, arg):
		data = get("https://api.mcsrvstat.us/2/{}".format(arg)).json()
		if data['online']:
			embed = Embed(
				title="Minecraft Server Check",
				description="The server is online!",
				url='https://mcsrvstat.us/server/{}'.format(arg),
				colour=0x7ED6DE)
			if data['hostname'] != arg:
				embed.add_field(name='Host', value=data['hostname'], inline=False)
			if data['port'] == 25565:
				embed.add_field(name='Direct IP', value=data['ip'], inline=False)
			else:
				embed.add_field(name='Direct IP', value='{}:{}'.format(data['ip'], data['port']), inline=False)
			embed.add_field(name='Players', value='{}/{}'.format(data['players']['online'], data['players']['max']), inline=False)
			embed.add_field(name='Version', value=str(data['version']), inline=False)
			open('data/decode.jpg', "wb+").write(b64decode(data['icon'].split(',')[1]))
			embed.set_thumbnail(url='attachment://decode.jpg')
			embed.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=embed, file=File('data/decode.jpg'))
		if not data['ip']:
			embed = Embed(
				title="Minecraft Server Check",
				description="Not found.",
				url='https://mcsrvstat.us/server/{}'.format(arg),
				colour=0x7ED6DE)
			embed.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=embed)
		if data['online'] == False:
			embed = Embed(
				title="Minecraft Server Check",
				description="The server is offline...",
				url='https://mcsrvstat.us/server/{}'.format(arg),
				colour=0x7ED6DE)
			if data['hostname'] != arg:
				embed.add_field(name='Host', value=data['hostname'], inline=False)
			if data['port'] == 25565:
				embed.add_field(name='Direct IP', value=data['ip'], inline=False)
			else:
				embed.add_field(name='Direct IP', value='{}:{}'.format(data['ip'], data['port']), inline=False)
			embed.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=embed)
			self.bot.data['smessages'] += 1

def setup(bot: Bot):
    bot.add_cog(Minecraft(bot))