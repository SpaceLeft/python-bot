from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context
import settings as s
from lib import data
from requests import post, get
from asyncio import sleep
from datetime import datetime, timedelta
from discord_slash import cog_ext, SlashContext
import psutil
from threading import active_count

class Status(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.bot.loop.create_task(self.systemstatus())
		self.nodes = ['1-1', '1-2', '1-3', '1-4', '1-5', '1-6', '1-7', '1-8', '2-1', '2-2', '2-3', '2-4', '2-5', '2-6', '2-7', '2-8', '2-9', '2-10', '2-11', '2-12']

	@cog_ext.cog_slash(name='ping', description='Send Latency')
	async def _ping(self, ctx: SlashContext):
		before = datetime.now()
		message = await ctx.send('Pong!')
		after = datetime.now()
		response = post('https://discord.com/api/oauth2/authorize', timeout=3)
		embed = Embed(title='Ping', colour=data.color1)
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

	async def systemstatus(self):
		channel = self.bot.get_channel(918558401812901888)
		await channel.purge(limit=100)
		while True:
			try:
				await sleep(1.95)
				net = psutil.net_io_counters(pernic=True)
				embed = Embed(title='Bot Status', colour=0x3498db, timestamp=datetime.utcnow())
				nodes = 0
				players = []
				us = 0
				eu = 0
				downnodes = []
				for node in self.nodes:
					try:
						temp = self.bot.nodes.get_node(identifier=node)
						if temp.is_available:
							nodes += 1
							if node.startswith('2-'):
								eu += 1
							else:
								us += 1
						else:
							downnodes.append(node)
						players += temp.players
					except:
						downnodes.append(node)
				embed.add_field(name='Ping', value='**Client** : {:.2f}ms\n**WebSocket** : {:.2f}ms'.format(self.bot.latency*1000, post('https://discord.com/api/oauth2/authorize', timeout=3).elapsed.total_seconds()*1000), inline=False)
				embed.add_field(name='Version', value='{} ({})'.format(self.bot.log3[:-1], open('data/builds.txt', 'r', encoding='utf_8').read()), inline=False)
				embed.add_field(name='Nodes', value='{}/20 ( eu:{} | us:{} )'.format(nodes, eu, us), inline=False)
				embed.add_field(name='Players', value='{}'.format(len(players)), inline=False)
				embed.add_field(name='Threads (ReverseTranslation)', value='{} ({})'.format(active_count(), self.bot.rev), inline=False)
				embed.add_field(name='Errors', value='Coming soon...', inline=False)
				if downnodes:
					embed.add_field(name='Down Nodes', value='`{}`'.format('`,`'.join(downnodes)), inline=False)
				#embed.add_field(name='Nodes', value='{}/12'.format(nodes), inline=False)
				embed.add_field(name='CPU Usage', value='{:.1f}%'.format(psutil.cpu_percent()), inline=False)
				embed.add_field(name='Memory Usage', value='{:.1f}GB / {:.1f}GB ({}%)'.format(psutil.virtual_memory().used / 1024 / 1024 / 1024, psutil.virtual_memory().total / 1024 / 1024 / 1024, psutil.virtual_memory().percent), inline=False)
				try:
					try:
						send = int(net['Wi-Fi 2'].bytes_sent - nett['Wi-Fi 2'].bytes_sent)
						recieve = int(net['Wi-Fi 2'].bytes_recv - nett['Wi-Fi 2'].bytes_recv)
					except:
						try:
							send = int(net['イーサネット 2'].bytes_sent - nett['イーサネット 2'].bytes_sent)
							recieve = int(net['イーサネット 2'].bytes_recv - nett['イーサネット 2'].bytes_recv)
						except:
							try:
								send = int(net['Wi-Fi 3'].bytes_sent - nett['Wi-Fi 3'].bytes_sent)
								recieve = int(net['Wi-Fi 3'].bytes_recv - nett['Wi-Fi 3'].bytes_recv)
							except:
								send = int(net['eth0'].bytes_sent - nett['eth0'].bytes_sent)
								recieve = int(net['eth0'].bytes_recv - nett['eth0'].bytes_recv)
					embed.add_field(name='Network Usage', value='↑{:.1f}KB ↓{:.1f}KB'.format(send / 1024, recieve / 1024), inline=False)
				except:
					embed.add_field(name='Network Usage', value='Calculating...', inline=False)
				embed.add_field(name="Uptime", value=timedelta(seconds=int(datetime.utcnow().timestamp() - self.bot.starttime)), inline=False)
				embed.set_footer(text='Update Interval : 2s')
				try:
					await ms.edit(content=None, embed=embed)
					nett = net
				except:
					try:
						await ms.delete()
					except:
						pass
					ms = await self.bot.get_channel(918558401812901888).send(embed=embed)
			except Exception as e:
				self.bot.log(2, e)

	@command()
	async def ping(self, ctx: Context):
		before = datetime.now()
		message = await ctx.send('Pong!')
		after = datetime.now()
		response = post('https://discord.com/api/v6', timeout=3)
		embed = Embed(title='Ping', colour=data.color1)
		embed.add_field(name='Response', value='{:.2f}ms'.format((after.timestamp()-before.timestamp())*1000), inline=False)
		embed.add_field(name='Client', value='{:.2f}ms'.format(self.bot.latency*1000), inline=False)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000), inline=False)
		await message.edit(content=None, embed=embed)

def setup(bot: Bot):
    bot.add_cog(Status(bot))
