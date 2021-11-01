from discord import Embed, File
from discord.ext.commands import Bot, Cog, command, Context
from requests import get
from base64 import b64decode

class Checker(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		
	@command(aliases=['check', 'servercheck', 'ch'])
	async def mccheck(self, ctx: Context, arg):
		data = get("https://api.mcsrvstat.us/2/{}".format(arg)).json()
		if data['online'] == True:
			sendms = Embed(
			    title="Minecraft Server Check",
			    description="The server is online!",
			    url='https://mcsrvstat.us/server/{}'.format(arg),
			    colour=0x7ED6DE)
			sendms.add_field(
			    name='Hostname', value=str(data['hostname']), inline=False)
			sendms.add_field(
			    name='IP Address', value=str(data['ip']), inline=False)
			sendms.add_field(
			    name='Port', value=str(data['port']), inline=False)
			sendms1 = str(data['players']['online']) + '/' + str(
			    data['players']['max'])
			sendms.add_field(name='Players', value=str(sendms1), inline=False)
			sendms.add_field(
			    name='Version', value=str(data['version']), inline=False)
			with open('data/decode.jpg', "wb+") as f:
				f.write(b64decode(str(data['icon'].split(',')[1])))
			thumbnail = await self.bot.get_channel(793030006221307915).send(file=File('data/decode.jpg'))
			sendms.set_thumbnail(url=thumbnail.attachments[0].url)
			sendms.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=sendms)
		if data['ip'] == data['port']:
			sendms = Embed(
			    title="Minecraft Server Check",
			    description="Not found.",
			    url='https://mcsrvstat.us/server/{}'.format(arg),
			    colour=0x7ED6DE)
			sendms.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=sendms)
		if data['online'] == False:
			sendms = Embed(
			    title="Minecraft Server Check",
			    description="The server is offline...",
			    url='https://mcsrvstat.us/server/{}'.format(arg),
			    colour=0x7ED6DE)
			sendms.add_field(
			    name='Hostname', value=str(data['hostname']), inline=False)
			sendms.add_field(
			    name='IP Address', value=str(data['ip']), inline=False)
			sendms.add_field(
			    name='Port', value=str(data['port']), inline=False)
			sendms.set_footer(text='Powered by mcsrvstats.us')
			await ctx.send(embed=sendms)

def setup(bot: Bot):
    bot.add_cog(Checker(bot))