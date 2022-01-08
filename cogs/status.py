from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context
import settings as s
from lib import data
from requests import post, get
from asyncio import sleep
from datetime import datetime, timedelta
from discord_slash import cog_ext, SlashContext
import psutil

template_bot = '''```
CPU
{0.cpu_progress} {0.cpu:.1f}%
Memory ({0.memory_used:.1f}GB/{0.memory_total:.1f}GB)
{0.memory_progress} {0.memory_usage:.1f}%
Network : ↑{0.network_send:.1f}KB ↓{0.network_recieve:.1f}KB
Threads : {0.threads} (Rev {0.rev})

OS : {0.platform}
Version : {0.version}
Messages : {0.messages}
Ping : {0.ping:.2f}ms
Downnodes : {1}
Uptime : {0.uptime}
```'''

template_node = '''```
CPU
{0.cpu_progress} {0.cpu:.2f}%
Memory ({0.memory_used:.1f}MB/{0.memory_allocated:.1f}MB)
{0.memory_progress} {0.memory_percent:.2f}%
Lavalink Load
{0.lavalink_progress} {0.lavalink_load:.2f}%

Uptime : {0.uptime}
Players : {0.players}
Penalty : {0.penalty:.2f}
Region : {0.region}
```'''

class Status(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	@cog_ext.cog_slash(name='ping', description='Send Latency')
	async def _ping(self, ctx: SlashContext):
		before = datetime.now()
		message = await ctx.send('Pong!')
		self.bot.data['smessages'] += 1
		after = datetime.now()
		response = post('https://discord.com/api/oauth2/authorize', timeout=3)
		embed = Embed(title='Ping', colour=data.color1)
		embed.add_field(name='Response', value='{:.2f}ms'.format((after.timestamp()-before.timestamp())*1000))
		embed.add_field(name='Client', value='{:.2f}ms'.format(self.bot.latency*1000))
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000))
		await message.edit(content=None, embed=embed)

	def savedata(self):
		interval = 60
		data = open('data/data.json', 'r').read()

	@Cog.listener()
	async def on_message(self, message):
		self.bot.data['rmessages'] += 1

	@Cog.listener()
	async def on_ready(self):
		await self.bot.loop.run_in_executor(None, self.savedata)
		interval = 2
		if self.bot.user.id == 907167351634542593:
			ms = await self.bot.get_channel(918558401812901888).fetch_message(929433145114263633)
		if self.bot.user.id == 907531399433715752:
			ms = await self.bot.get_channel(768763368692776970).send('a')
		nett = None
		while True:
			try:
				await sleep(interval)
				net = psutil.net_io_counters(pernic=True)
				node = data.get_nodes(self.bot)
				user = data.countuser(self)
				embed = Embed(title='Node Status', colour=0x3498db, timestamp=datetime.utcnow())
				for w in node['nodes']:
					embed.add_field(name="Node-{}".format(w.identifier), value=template_node.format(data.stats(w)), inline=False)
				embed.set_footer(text=f'Update Interval : {interval}s')
				if node['downnodes']:
					downnodes = '`{}`'.format('`,`'.join(node['downnodes']))
				else:
					downnodes = None
				embed.add_field(name='Bot', value=template_bot.format(data.botstats(self.bot, interval, net, nett), downnodes))
				embed.set_footer(text=f'Update Interval : {interval}s')
				await ms.edit(content=None, embed=embed)
				nett = net
			except Exception as e:
				self.bot.log(2, e)
		
	@command(aliases=[])
	async def status(self, ctx: Context):
		desc= ['**Main : :green_square: Online**\n', '**[Web](https://akishoudayo.herokuapp.com/) : :black_large_square: Checking...**\n', '**[Music-1](https://commandnetworkmusic1.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-2](https://commandnetworkmusic2.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-3](https://commandnetworkmusic3.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-4](https://commandnetworkmusic4.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-5](https://commandnetworkmusic5.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-6](https://commandnetworkmusic6.herokuapp.com/) : :black_large_square: Checking...**\n',  '**[Music-7](https://commandnetworkmusic7.herokuapp.com/) : :black_large_square: Checking...**\n', '**[Discord API](https://discord.com/api/oauth2/authorize?client_id=761929481421979669&permissions=8&response_type=code&scope=bot%20applications.commands) : :black_large_square: Checking...**\n', '**[mcsrvstat.us](https://api.mcsrvstat.us) : :black_large_square: Checking...**']
		embed = Embed(title='Status', description=''.join(desc), colour=s.color1)
		message = await ctx.send(embed=embed)
		self.bot.data['smessages'] += 1
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
		embed = Embed(title='Ping', colour=data.color1)
		embed.add_field(name='Response', value='{:.2f}ms'.format((after.timestamp()-before.timestamp())*1000), inline=False)
		embed.add_field(name='Client', value='{:.2f}ms'.format(self.bot.latency*1000), inline=False)
		embed.add_field(name='API', value='{:.2f}ms'.format(response.elapsed.total_seconds()*1000), inline=False)
		await message.edit(content=None, embed=embed)
		self.bot.data['smessages'] += 1

def setup(bot: Bot):
    bot.add_cog(Status(bot))
