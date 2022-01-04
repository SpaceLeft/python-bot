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

async def on_socket_response(msg):
	if msg["t"] != "INTERACTION_CREATE":
		return

disable = 'music2'
class bot(Bot):
	def __init__(self):
		self.mention = AllowedMentions(replied_user=False)
		super().__init__(command_prefix=when_mentioned_or(getenv('PREFIX')), intents=Intents.all(), activity=Activity(name="Loading...", type=3), allowed_mentions=self.mention, help_command=None)
		self.log = logging.setup()
		self.data = {'start': datetime.utcnow().timestamp(), 'rev': {}, 'user': 0, 'userbot':0, 'version': None}
		self.data['password'] = getenv('PASSWORD')
		address = get('https://raw.githubusercontent.com/akishoudayo/python-bot/master/address.txt').text.split('\n')
		self.data['nodes'] = []
		node_count = 1
		for node in address:
			self.data['nodes'].append({"host": node, "port": 80, "name": str(node_count)})
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
		self.add_listener(on_socket_response)
		await self.change_presence(activity=Activity(name="{}help | {}".format(getenv('PREFIX'), self.data['version']), type=3))

if __name__ == "__main__":
    bot = bot()
    bot.run(getenv('TOKEN'), reconnect=True)