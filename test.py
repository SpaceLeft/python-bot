from pathlib import Path
from discord import Embed, Activity, Intents, Status, AllowedMentions
from discord.ext.commands import Bot, when_mentioned_or
from datetime import timezone, timedelta
from discord_slash import SlashCommand
import logging
import settings as s
from lib import logging, slash
from datetime import datetime
from sys import excepthook, stderr, exit
from asyncio import sleep

def error_handler(a, b, c):
	now = datetime.now().strftime('%H:%M:%S')
	print('[{}] [Traceback] : {}'.format(now, b), file=stderr)

excepthook = error_handler

class MyBot(Bot):
	def __init__(self):
		JST = timezone(timedelta(hours=+9), 'JST')
		self.mention = AllowedMentions(replied_user=False)
		super().__init__(command_prefix=when_mentioned_or(s.prefix),intents=Intents.all(), activity=Activity(name="Loading...", type=3), allowed_mentions=self.mention, help_command=None)
		#self.slash = SlashCommand(self, sync_commands=True)
		self.log = logging.setup()
		for cog in Path("cogs/").glob("*.py"):
			try:
				if cog.stem != 'network':
					self.load_extension("cogs." + cog.stem)
					self.log(1, f"Loaded Extension ({cog.stem}.py)")
			except Exception as e:
				self.log(4, e)

if __name__ == "__main__":
	bot = MyBot()
