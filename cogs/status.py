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

template = '''
Uptime : {0.uptime}
Players : {0.players}

CPU : {0.cpu:.2f}%
Memory : {0.memory_used:.1f}MB / {0.memory_allocated:.1f}MB
Frames : Sent {0.frames_sent:.1f}k
         Nulled {0.frames_nulled:.1f}k
         Failed {0.frames_deficit:.1f}k
Lavalink : {0.lavalink_load:.2f}%
'''

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
			ms = await self.bot.get_channel(918558401812901888).fetch_message(928027610334777414)
		if self.bot.user.id == 907531399433715752:
			ms = await self.bot.get_channel(768763368692776970).send('a')
		while True:
			try:
				await sleep(interval)
				net = psutil.net_io_counters(pernic=True)
				node = data.get_nodes(self.bot)
				user = data.countuser(self)
				embed = Embed(title='Status', colour=0x3498db, timestamp=datetime.utcnow())
				embed.add_field(name='Ping', value='**Client** : {:.2f}ms\n**API** : {:.2f}ms'.format(self.bot.latency*1000, data.ping()), inline=False)
				embed.add_field(name='Version', value='{} ({})'.format(self.bot.log3[:-1], open('data/builds.txt', 'r', encoding='utf_8').read()), inline=False)
				for w in node['nodes']:
					embed.add_field(name="Node-{}".format(w.identifier), value='```{}```'.format(template[1:].format(data.stats(w))), inline=False)
				embed.add_field(name='Players', value='{}'.format(node['players']), inline=False)
				embed.add_field(name='Threads (ReverseTranslation)', value='{} ({})'.format(active_count(), len(self.bot.data['rev'])), inline=False)
				embed.add_field(name='Errors', value='Coming soon...', inline=False)
				if node['downnodes']:
					embed.add_field(name='Down Nodes', value='`{}`'.format('`,`'.join(downnodes)), inline=False)
				embed.add_field(name='Message', value='↑{} ↓{}'.format(self.bot.data['smessages'], self.bot.data['rmessages']), inline=False)
				embed.add_field(name='Environment', value='Python {}, Java 13'.format(data.version), inline=False)
				embed.add_field(name='System', value=data.platform, inline=False)
				embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=False)
				embed.add_field(name='Users (All)', value='{} ({})'.format(user['user'], user['userbot']), inline=False)
				embed.add_field(name='CPU Usage', value='{:.1f}%'.format(psutil.cpu_percent()), inline=False)
				embed.add_field(name='Memory Usage', value='{:.1f}GB / {:.1f}GB ({}%)'.format(psutil.virtual_memory().used / 1024 / 1024 / 1024, psutil.virtual_memory().total / 1024 / 1024 / 1024, psutil.virtual_memory().percent), inline=False)
				try:
					send,recieve = data.net(net, nett)
					embed.add_field(name='Network Usage', value='↑{:.1f}KB ↓{:.1f}KB'.format(send / 1024 / interval, recieve / 1024 / interval), inline=False)
				except:
					embed.add_field(name='Network Usage', value='Calculating...', inline=False)
				embed.add_field(name="Uptime", value=timedelta(seconds=int(datetime.utcnow().timestamp() - self.bot.data['start'])), inline=False)
				embed.set_footer(text=f'Update Interval : {interval}s')
				nett = net
				await ms.edit(content=None, embed=embed)
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
