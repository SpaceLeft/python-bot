from requests import get, post
import settings as s
from functools import partial as fpartial
from json import loads
from discord.ext import commands
from datetime import timedelta
from asyncio import BaseEventLoop, get_event_loop
from platform import python_version, platform

language = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg','ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el','gu', 'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig','id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky','lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi','mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa','ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl','so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk','ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']

color1 = 0x377EF0 #blue
color2 = 0xF8C63D #yellow
color3 = 0x1A8FE3 #aqua
color4 = 0xFF0000 #red
blue = 0x377EF0 #blue
yellow = 0xF8C63D #yellow
aqua = 0x1A8FE3 #aqua
error = 0xFF0000 #red
temp = platform(terse=False).split('-')
platform = '{} {} ({})'.format(temp[0], temp[1], '-'.join(temp[2:]))
version = python_version()

class stats:
    def __init__(self, node):
        self.uptime = timedelta(milliseconds=node.stats.uptime)
        self.players = len(node.players)
        self.name = f'Node-{node.identifier}'
        self.cpu = node.stats.system_load*100
        self.memory_used = node.stats.memory_used/1048576
        self.memory_allocated = node.stats.memory_allocated/1048576
        self.frames_sent = node.stats.frames_sent/1000
        self.frames_nulled = node.stats.frames_nulled/1000
        self.frames_deficit = node.stats.frames_deficit/1000
        self.lavalink_load = node.stats.lavalink_load*100

def net(net, nett):
    if 'eth0' in net:
        send = int(net['eth0'].bytes_sent - nett['eth0'].bytes_sent)
        recieve = int(net['eth0'].bytes_recv - nett['eth0'].bytes_recv)
    if 'Wi-Fi 2' in net:
        send = int(net['Wi-Fi 2'].bytes_sent - nett['Wi-Fi 2'].bytes_sent)
        recieve = int(net['Wi-Fi 2'].bytes_recv - nett['Wi-Fi 2'].bytes_recv)
    if 'イーサネット 2' in net:
        send = int(net['イーサネット 2'].bytes_sent - nett['イーサネット 2'].bytes_sent)
        recieve = int(net['イーサネット 2'].bytes_recv - nett['イーサネット 2'].bytes_recv)
    if 'Wi-Fi 3' in net:
        send = int(net['Wi-Fi 3'].bytes_sent - nett['Wi-Fi 3'].bytes_sent)
        recieve = int(net['Wi-Fi 3'].bytes_recv - nett['Wi-Fi 3'].bytes_recv)
    return send, recieve

def ping():
    return post('https://discord.com/api/oauth2/authorize', timeout=2).elapsed.total_seconds() * 1000

def progressbar(current, max):
    ratio = current / max
    length = 20
    progress = int(ratio * length)
    bar =  f'[{"=" * progress}{" " * (length - progress)}]'
    percentage = int(ratio * 100)
    return f'{bar}'# {percentage}%'

def percent(current, max):
    ratio = current / max
    percentage = int(ratio * 100)
    return percentage

def get_nodes(bot):
    result = {'players':0, 'count': 0, 'nodes': [], 'downnodes': []}
    for n in range(1, len(bot.data['address'])):
        node = bot.nodes.get_node(identifier=str(n))
        if node.is_available:
            result['count'] += 1
            result['nodes'].append(node)
        else:
            result['downnodes'].append(str(n))
        result['players'] += len(node.players)
    return result


def countuser(self):
    user_count = []
    user_bot_count = []
    for guild in self.bot.guilds:
        for member in guild.members:
            user_bot_count.append(member.id)
            if not member.bot:
                user_count.append(member.id)
    return {'user': len(user_count), 'userbot': len(user_bot_count)}

def duration(value: int):
    if value < 1:
        return '0:00'
    minutes, seconds = divmod(int(value), 60)
    hours, minutes = divmod(int(minutes), 60)
    days, hours = divmod(int(hours), 24)
    temp = []
    if days > 0:
        temp.append('{}d, '.format(days))
    if hours > 0:
        temp.append('{}:'.format(hours))
    if minutes > 0:
        if hours > 0:
            temp.append('{}:'.format(str(minutes).zfill(2)))
        else:
            temp.append('{}:'.format(minutes))
    if minutes < 1:
        temp.append('0:')
    if seconds > 0:
        temp.append('{}'.format(str(seconds).zfill(2)))
    if seconds == 0:
        temp.append('00')
    return ''.join(temp)

def download(search):
    try:
        data = get('https://akishoudayo-database.herokuapp.com/ytdl?url={}'.format(search))
        return loads(data.text)
    except:
        return

class Downloader:
    def __init__(self, ctx: commands.Context, *, data: dict):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        try:
            self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        except:
            pass
        self.title = data.get('title')
        try:
            self.thumbnail = data['thumbnails'][0]['url']
        except:
            self.thumbnail = None
        self.description = data.get('description')
        self.duration = data.get('duration2')
        self.intduration = data.get('duration')
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')
        self.bitrate = data.get('bitrate')
        self.opus = data.get('opus')
        self.artist = data.get('artist')
        self.file = data.get('file')
        self.extractor = data.get('extractor')
        self.id = data.get('id')

    @classmethod
    async def create_source(cls, ctx: commands.Context, loop: BaseEventLoop = None, *, search: str):
        loop = loop or get_event_loop()
        data = await loop.run_in_executor(None, fpartial(download, search))
        if not data:
            await ctx.send('**Not Found Videos : `{}`**'.format(search))
        return cls(ctx, cls.FFMPEG_OPTIONS, data=data)