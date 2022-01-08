from pathlib import Path
from discord import Embed, Activity, Intents, Status, AllowedMentions
from discord.ext.commands import Bot, when_mentioned_or
from datetime import timedelta
import settings as s
from datetime import datetime
from os import getenv
from requests import get
from lib import build, logging#, slash
from traceback import print_exc
from json import loads

disable = ''
class bot(Bot):
	def __init__(self):
		self.mention = AllowedMentions(replied_user=False)
		super().__init__(command_prefix=when_mentioned_or(getenv('PREFIX')), intents=Intents.all(), activity=Activity(name="Loading...", type=3), allowed_mentions=self.mention, help_command=None)
		self.log = logging.setup()
		self.exit = False
		self.data = {'start': datetime.utcnow().timestamp(), 'rev': {}, 'user': 0, 'userbot':0, 'version': None, 'smessages':0, 'rmessages': 0}
		self.data['password'] = getenv('PASSWORD')
		self.data['address'] = loads(open('address.txt', 'r').read())
		#self.data['address'] = get('https://raw.githubusercontent.com/akishoudayo/python-bot/master/address.txt').json()
		print('\n'.join(self.data['address']))
		print(open('address.txt', 'r').read())
		self.data['nodes'] = []
		node_count = 1
		for region in self.data['address'].keys():
			for node in self.data['address'][region]:
				print(f'{node} : {region}')
				self.data['nodes'].append({"host": node, "port": 80, "name": str(node_count), "region": region})
				node_count += 1
		for cog in Path("cogs/").glob("*.py"):
			try:
				if disable.find(cog.stem) == -1:
					self.load_extension("cogs." + cog.stem)
					self.log(1, f"Loaded Extension ({cog.stem}.py)")
			except Exception as e:
				print_exc()
		#self.slash = slash.setup(self)
		
	async def on_ready(self):
		self.data['headers'] = {
            "Authorization": "Bot " + getenv("TOKEN")
        }
		user = []
		for guild in self.guilds:
			for member in guild.members:
				if not member.bot:
					user.append(member.id)
		self.data['user'] = len(user)
		self.log(1, 'Logged In Successful ({} Users)'.format(len(user)))
		await self.change_presence(activity=Activity(name="{}help | {}".format(getenv('PREFIX'), self.data['version']), type=3))

if __name__ == "__main__":
	bot = bot()
	try:
		bot.run(getenv('TOKEN'), reconnect=True)
	except Exception as e:
		if e == KeyboardInterrupt:
			bot.log(4, 'KeyboardInterrupt')
			bot.exit = True
		else:
			bot.log(4, e)
