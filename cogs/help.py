from discord import Embed
from discord.ext.commands import Bot, Cog, command, Context, CommandError, UserInputError, CommandNotFound, BotMissingPermissions, CommandOnCooldown, MissingPermissions, CheckFailure, NoPrivateMessage
from sys import version
import settings as s
from re import sub
from lib import data
from sys import exc_info
from datetime import datetime as d, timedelta
from platform import python_version, platform


class Help(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.data['modules'] = ['discord(discord.py)', 'PyNaCl', 'youtube_dl', 'requests', 'asyncio',
                        'discord-py-slash-command', 'discord-py-interactions', 'flask', 'wavelink', 'base64',
                        'platform', 'random', 'sys', 'os', 'functools', 'ast', 'subprocess', 're', 'datetime', 'time']
        self.bot.data['commands'] = ['random', 'choice', 'say', 'help', 'servercheck', 'play', 'omikuji', 'info', 'ping', 'reversetranslate', 'translate',
                         'status', 'seek', 'queue', 'skip', 'volume', 'bassboost', 'eq', 'nowplaying', 'repeat',
                         'shuffle', 'support', 'invite', 'join', 'leave']


    @command(aliases=['info'])
    async def information(self, ctx: Context, arg=None):
        embed = Embed(title='Information', colour=data.color1)
        embed.add_field(name='Version', value=self.bot.log3[:-1], inline=False)
        embed.add_field(name='Environment', value='Python {}, Java 11'.format(python_version()), inline=False)
        temp = platform(terse=False).split('-')
        embed.add_field(name='System', value='{} {}({})'.format(temp[0], temp[1], '-'.join(temp[2:])), inline=False)
        embed.add_field(name="Number of Commands", value=str(len(self.bot.data['commands'])), inline=False)
        embed.add_field(name="Number of Guilds", value=str(len(self.bot.guilds)), inline=False)
        embed.add_field(name="Number of Modules", value=str(len(self.bot.data['modules'])), inline=False)
        user_count = []
        user_bot_count = []
        for guild in self.bot.guilds:
            for member in guild.members:
                user_bot_count.append(member.id)
                if not member.bot:
                    user_count.append(member.id)
        self.bot.data['user'] = len(user_count)
        self.bot.data['userbot'] = len(user_bot_count)
        embed.add_field(name="Number of Users", value='{} (All : {})'.format(self.bot.data['user'], self.bot.data['userbot']), inline=False)
        embed.add_field(name="Number of Builds", value=open('data/builds.txt', 'r', encoding='utf_8').read(), inline=False)
        embed.add_field(name="Uptime", value=timedelta(seconds=int(d.utcnow().timestamp() - self.bot.starttime)), inline=False)
        embed.add_field(name="Language", value="English, Japanese", inline=False)
        embed.add_field(name="Official Site", value="https://akishoudayo.herokuapp.com/", inline=False)
        await ctx.send(embed=embed)


    @Cog.listener()
    async def on_message(self, message):
        if message.content == self.bot.user.mention:
            await self._help(message.channel)


    @Cog.listener()
    async def on_command_error(self, ctx, value):
        self.bot.log(4, value)
        error = getattr(value, 'original', value)
        if isinstance(error, CommandNotFound):
            return
        if isinstance(error, CommandError):
            embed = Embed(title='Error', description=value, color=data.color4)
            await ctx.send(embed=embed)
            return
        if isinstance(error, BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            await ctx.send('I need the **{}** permission(s) to run this command.'.format(fmt))
            return
        if isinstance(error, CommandOnCooldown):
            await ctx.send("This command is on cooldown. Please retry in {}s.".format(math.ceil(error.retry_after)))
            return
        if isinstance(error, MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            await ctx.send('You need the **{}** permission(s) to use this command.'.format(fmt))
            return
        if isinstance(error, UserInputError):
            embed = Embed(title='Error', description=value, color=data.color4)
            await ctx.send(embed=embed)
            return
        if isinstance(error, NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass


    @command(aliases=[])
    async def help(self, ctx: Context, arg=None):
        if not arg:
            embed = Embed(title="Command List", description='Prefix : `c.`', color=0x00ffff, timestamp=d.utcnow())
            embed.add_field(name='Support/Help', value='~~`support`~~,~~`invite`~~,`help`,~~`about`~~,~~`report`~~,~~`request`~~', inline=False)
            #,`bassboost(beta)`,`remove`
            embed.add_field(name='Music',value='`play`,`nowplaying`,`volume`,`queue`,`skip`,`shuffle`,`join`,`leave`,`seek`,`search`',inline=False)
            embed.add_field(name='Fun', value='~~`random`~~,~~`say`~~,~~`choice`~~,`reversetranslate`,`omikuji`', inline=False)
            embed.add_field(name='Tool', value='~~`googlesearch`~~,~~`timer`~~,`servercheck`,~~`time`~~,~~`downloader`~~,`translator`,~~`uploader`~~',inline=False)
            if ctx.author.id == 749013126866927713 or ctx.author.id == 897030094290321468:
                embed.add_field(name='Admin', value='`reload`,`load`,`unload`,`eval`')
            embed.add_field(name='Status', value='`ping`,~~`status`~~,`information`', inline=False)
            #embed.set_footer(text='More help : c.help <command>')
            await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Help(bot))
