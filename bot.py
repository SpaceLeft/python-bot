from pathlib import Path
from discord import Embed, Activity, Intents, Status, AllowedMentions
from discord.ext.commands import Bot, when_mentioned_or
from datetime import timezone, timedelta
import settings as s
from datetime import datetime
from os import getenv
from lib import build, logging#, slash

disable = 'music1, music3, checker'

class Bot(Bot):
	def __init__(self):
		self.mention = AllowedMentions(replied_user=False)
		super().__init__(command_prefix=when_mentioned_or(getenv('PREFIX')), intents=Intents.all(), activity=Activity(name="Loading...", type=3), allowed_mentions=self.mention, help_command=None)
		self.log = logging.setup()
		for cog in Path("cogs/").glob("*.py"):
			try:
				if disable.find(cog.stem) == -1:
					self.load_extension("cogs." + cog.stem)
					self.log(1, f"Loaded Extension ({cog.stem}.py)")
			except Exception as e:
				self.log(4, e)
		self.data = {'rev': {}, 'user': 0, 'version': self.log3[:-1]}
		#self.slash = slash.setup(self)
		
	async def on_ready(self):
		self.starttime = datetime.utcnow().timestamp()
		user = []
		for guild in self.guilds:
			for member in guild.members:
				if not member.bot:
					user.append(member.id)
		self.data['user'] = len(user)
		self.log(1, 'Logged In Successful ({} Users)'.format(len(user)))
		await self.change_presence(activity=Activity(name="{}help | {}".format(getenv('PREFIX'), self.log3[:-1]), type=3))

if __name__ == "__main__":
    bot = Bot()
    bot.run(getenv('TOKEN'), reconnect=True)