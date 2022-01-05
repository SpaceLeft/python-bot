from requests import post as rpost
from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context

class Translator(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
	@command(aliases=['t','trans','translate'])
	async def translator(self, ctx: Context, *, args):
		message = await ctx.reply('翻訳しています...', mention_author=False)
		self.bot.data['smessages'] += 1
		arg = args.split(' ')
		if arg[0].find('>') != -1:
			lang = arg[0].split('>')
			params = {
				"auth_key": "fda425ee-b88a-2b15-75c1-ffcf57a14007:fx", 
				"text": str(' '.join(arg[1:])), 
				"source_lang": lang[0],
				"target_lang": lang[1]
			}
			lang = lang[1]
		else:
			params = {
				"auth_key": "fda425ee-b88a-2b15-75c1-ffcf57a14007:fx", 
				"text": str(' '.join(arg[1:])), 
				"target_lang": arg[0]
			}
			lang = arg[0]
		result = rpost("https://api-free.deepl.com/v2/translate", data=params).json()
		sendms = Embed(title='Result', description='{}\n({} > {})'.format(result['translations'][0]['text'], result['translations'][0]['detected_source_language'], lang))
		sendms.set_footer(text='Powered by DeepL Translator')
		await message.edit(content=None, embed=sendms, allowed_mentions=self.bot.mention)

def setup(bot: Bot):
    bot.add_cog(Translator(bot))