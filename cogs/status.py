from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context
import settings as s
from requests import post, get
from datetime import datetime
from discord_slash import cog_ext, SlashContext

class Status(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
	
	@cog_ext.cog_slash(name='ping', description='Send Latency')
	async def _ping(self, ctx: SlashContext):
		before = datetime.now()
		message = await ctx.send('Pong!')
		after = datetime.now()
		response = post('https://discord.com/api/oauth2/authorize', timeout=3)
		embed = Embed(title='Ping', colour=s.color1)
		embed.add_field(name='Response', value='{:.2f}ms'.format((after.timestamp()-before.timestamp())*1000))
		embed.add_field(name='Client', value='{:.2f}ms'.format(self.bot.latency*1000))
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		await message.edit(content=None, embed=embed)
		
	@command(aliases=[])
	async def status(self, ctx: Context):
		desc= ['**Main : :green_square: Online**\n', '**[Web](https://akishoudayo.herokuapp.com/) : :black_large_square: Checking...**\n', '**[Music-1](https://commandnetworkmusic1.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-2](https://commandnetworkmusic2.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-3](https://commandnetworkmusic3.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-4](https://commandnetworkmusic4.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-5](https://commandnetworkmusic5.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-6](https://commandnetworkmusic6.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-7](https://commandnetworkmusic7.herokuapp.com/) : :black_large_square: Checking...**\n', '**[Discord API](https://discord.com/api/oauth2/authorize?client_id=761929481421979669&permissions=8&response_type=code&scope=bot%20applications.commands) : :black_large_square: Checking...**\n', '**[mcsrvstat.us](https://api.mcsrvstat.us) : :black_large_square: Checking...**']
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		message = await ctx.send(embed=embed)
		response = post('https://akishoudayo.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[1] = '**[Web](https://akishoudayo.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[1] = '**[Web](https://akishoudayo.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		await message.edit(content=None, embed=embed)
		response = post('https://commandnetworkmusic1.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[2] = '**[Music-1](https://commandnetworkmusic1.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[2] = '**[Music-1](https://commandnetworkmusic1.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		response = post('https://commandnetworkmusic2.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[3] = '**[Music-2](https://commandnetworkmusic2.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[3] = '**[Music-2](https://commandnetworkmusic2.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		response = post('https://commandnetworkmusic3.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[4] = '**[Music-3](https://commandnetworkmusic3.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[4] = '**[Music-3](https://commandnetworkmusic3.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		response = post('https://commandnetworkmusic4.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[5] = '**[Music-4](https://commandnetworkmusic4.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[5] = '**[Music-4](https://commandnetworkmusic4.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		await message.edit(content=None, embed=embed)
		response = post('https://commandnetworkmusic5.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[6] = '**[Music-5](https://commandnetworkmusic5.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[6] = '**[Music-5](https://commandnetworkmusic5.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		response = post('https://commandnetworkmusic6.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[7] = '**[Music-6](https://commandnetworkmusic6.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[7] = '**[Music-6](https://commandnetworkmusic6.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		response = post('https://commandnetworkmusic7.herokuapp.com/', timeout=3)#405on 503off
		if response.status_code == 503:
			desc[8] = '**[Music-7](https://commandnetworkmusic7.herokuapp.com/) : :red_square: Offline**\n'
		else:
			desc[8] = '**[Music-7](https://commandnetworkmusic7.herokuapp.com/) :  :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		await message.edit(content=None, embed=embed)
		response = get('https://discord.com/api/oauth2/authorize?client_id=761929481421979669&permissions=8&response_type=code&scope=bot%20applications.commands', timeout=3)
		if response.status_code == 200:
			desc[9] = '**[Discord API](https://discord.com/api/oauth2/authorize?client_id=761929481421979669&permissions=8&response_type=code&scope=bot%20applications.commands) : :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		else:
			desc[9] = '**[Discord API](https://discord.com/api/oauth2/authorize?client_id=761929481421979669&permissions=8&response_type=code&scope=bot%20applications.commands) : :red_square: Offline**\n'
		response = get('https://api.mcsrvstat.us/2/mc.hypixel.net', timeout=3)
		if response.status_code == 200:
			desc[10] = '**[mcsrvstat.us](https://api.mcsrvstat.us) : :green_square: Online** ({:.2f}ms)\n'.format(response.elapsed.total_seconds()*1000)
		iran = '''embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		response = post('https://heroku.com/', timeout=3)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		response = post('https://github.com/', timeout=3)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		response = post('https://api.hypixel.net/', timeout=3)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		response = post('https://api.mojang.com/', timeout=3)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))'''
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		await message.edit(content=None, embed=embed)
	
	@command()
	async def ping(self, ctx: Context):
		before = datetime.now()
		message = await ctx.send('Pong!')
		after = datetime.now()
		response = post('https://discord.com/api/v6', timeout=3)
		embed = Embed(title='Ping', colour=s.color1)
		embed.add_field(name='Response', value='{:.2f}ms'.format((after.timestamp()-before.timestamp())*1000), inline=False)
		embed.add_field(name='Client', value='{:.2f}ms'.format(self.bot.latency*1000), inline=False)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000), inline=False)
		await message.edit(content=None, embed=embed)

def setup(bot: Bot):
    bot.add_cog(Status(bot))