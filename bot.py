from pathlib import Path
from discord import Embed, Activity, Intents, Status, AllowedMentions
from discord.ext.commands import Bot, when_mentioned_or
from datetime import timezone, timedelta
import settings as s
from datetime import datetime
from os import getenv
from lib import build, logging#, slash
import traceback


class Bot(Bot):
	def __init__(self):
		self.mention = AllowedMentions(replied_user=False)
		super().__init__(command_prefix=when_mentioned_or(s.prefix), intents=Intents.all(), activity=Activity(name="Loading...", type=3), allowed_mentions=self.mention, help_command=None)
		self.log = logging.setup()
		#self.slash = slash.setup(self)
		
	async def on_ready(self):
		self.starttime = datetime.utcnow().timestamp()
		self.log(1, 'Logged In Successful')
		for cog in Path("cogs/").glob("*.py"):
			try:
				self.load_extension("cogs." + cog.stem)
				self.log(1, f"Loaded Extension ({cog.stem}.py)")
			except Exception as e:
				self.log(4, e)
				traceback.print_exc()
		await self.change_presence(activity=Activity(name="{}help | {}".format(s.prefix, self.log3[:-1]), type=3))

if __name__ == "__main__":
    bot = Bot()
    bot.run(getenv('TOKEN'), reconnect=True)