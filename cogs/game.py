from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context
from datetime import datetime as d, timedelta
from random import randint, choice
from googletrans import Translator
from lib import checker, data as s
from threading import Thread
from asyncio import sleep

class Game(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.result = {}

	def translate(self, num, arg, args):
		self.result['progress-{}'.format(num)] = 0
		for n in range(1, 3):
			try:
				translator = Translator()
				translator.translate('hello', dest='ja')
				break
			except Exception as e:
				self.bot.log(4, e)
				self.bot.log(2, 'Retrying... ({})'.format(n))
			if n == 3:
				raise Exception
		result = []
		if checker.debug == True:
			self.bot.log(1, '[RevTranslate] Translate Started')
		before = float(d.utcnow().timestamp())
		lang = choice(s.language)
		temp1 = translator.translate(args, dest=lang)
		temp2 = translator.translate(temp1.text, dest='ja')
		result.append(temp2.text)
		self.result['progress-{}'.format(num)] = '1/{} ({:.1f}%)'.format(arg, int(1*100)/int(arg))
		after = float(d.utcnow().timestamp())
		self.result['duration-{}'.format(num)] = int(float(after - before) * arg)
		for n in range(1, arg):
			before = float(d.utcnow().timestamp())
			lang = choice(s.language)
			temp1 = translator.translate(temp1.text, dest=lang)
			temp2 = translator.translate(temp1.text, dest='ja')
			result.append(temp2.text)
			if checker.debug == True:
				self.bot.log(3, '{} > {} (lang : {} > ja))'.format(temp1.text, temp2.text, lang))
			self.result['progress-{}'.format(num)] = '{}/{} ({:.1f}%)'.format(n+1, arg, int(int(n+1)*100)/int(arg))
			after = float(d.utcnow().timestamp())
			self.result['duration-{}'.format(num)] = int(float(after - before) * int(arg - int(n+1)))
			#self.bot.log(1, 'Position: {}'.format(n))
			#self.bot.log(1, 'Start: {}'.format(before))
			#self.bot.log(1, 'End: {}'.format(after))
			#self.bot.log(1, 'Duration: {}\n'.format(int(after - before) * int(arg - int(n+1))))
		if checker.debug == True:
			self.bot.log(1, '[RevTranslate] Translate Ended')
		self.result[num] = result

	@command(aliases=['rev', 're', 'reversetranslate'])
	async def reversetranslation(self, ctx: Context, arg: int, *, args: str):
		embed = Embed(title='逆翻訳しています...', colour=s.color1, timestamp=d.utcnow())
		embed.add_field(name='進行状況', value='0/{} (0.0%)'.format(arg), inline=False)
		embed.add_field(name='予想残り時間', value='計算中', inline=False)
		message = await ctx.reply(embed=embed, mention_author=False)
		for n in range(1, 3):
			num = str(randint(1, 9999))
			try:
				thread = Thread(target=self.translate, args=([num, arg, args]), name='Thread-{}'.format(num))
				thread.start()
				count = 0
				while True:
					try:
						if self.result[num] != None:
							break
					except:
						await sleep(1)
					count = count + 1
					if count == 3:
						count = 0
						try:
							embed = Embed(title='逆翻訳しています...', colour=s.color1, timestamp=d.utcnow())
							embed.add_field(name='進行状況', value=self.result['progress-{}'.format(num)], inline=False)
							embed.add_field(name='予想残り時間', value=timedelta(seconds=int(self.result['duration-{}'.format(num)])), inline=False)
							await message.edit(content=None, embed=embed, allowed_mentions=self.bot.mention)
						except:
							pass
				break
			except:
				if n == 3:
					await ctx.reply(content='Failed in Finalizing.')
					return
		embed = Embed(title='逆翻訳しています...', colour=s.color1, timestamp=d.utcnow())
		embed.add_field(name='進行状況', value='{0}/{0} (100%)'.format(arg), inline=False)
		embed.add_field(name='予想残り時間', value='完了', inline=False)
		await message.edit(content=None, embed=embed, allowed_mentions=self.bot.mention)
		finalize = []
		finalize2 = []
		finalize.append('{}\n'.format(args))
		for n in range(len(self.result[num])):
			if 4000 - len(''.join(finalize)) - len(self.result[num][n]) >= 100:
				finalize.append('\n{}. {}'.format(n+1, self.result[num][n]))
			elif 4000 - len(''.join(finalize2)) - len(self.result[num][n]) >= 100:
				finalize2.append('{}. {}\n'.format(n+1, self.result[num][n]))
			else:
				await ctx.reply(content='Error : The result is over 8000 characters.')
				return
		del self.result[num]
		embed = Embed(title='Result', description=''.join(finalize), colour=0x7ED6DE, timestamp=d.utcnow())
		await ctx.reply(embed=embed, mention_author=False)
		if len(finalize2) != 0:
			embed2 = Embed(title='Result', description=''.join(finalize2)[:-1], colour=0x7ED6DE, timestamp=d.utcnow())
			await ctx.send(embed=embed2)

	@command(aliases=[])
	async def omikuji(self, ctx: Context):
		now = datetime.now()
		temp = str(ctx.author.id % int(now.year * now.month * now.day))
		value = int(temp[len(temp)-1:])
		omikuji = ['大吉', '中吉', '小吉', '吉', '末吉', '凶', '小凶', '中凶', '大凶']
		if value == 0:
			result = omikuji[0]
		if value == 1:
			result = omikuji[1]
		if value == 2:
			result = omikuji[2]
		if value == 3:
			result = omikuji[3]
		if value == 4:
			result = omikuji[4]
		if value == 5:
			result = omikuji[1]
		if value == 6:
			result = omikuji[5]
		if value == 7:
			result = omikuji[0]
		if value == 8:
			result = omikuji[6]
		if value == 9:
			result = omikuji[7]
		embed = Embed(title='おみくじ', description='{}の結果\n\n`{}`'.format(now.strftime('%Y/%m/%d'), result), colour=s.color1, timestamp=datetime.utcnow())
		await ctx.send(embed=embed)

def setup(bot: Bot):
    bot.add_cog(Game(bot))