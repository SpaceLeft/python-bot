from requests import get
import settings as s
from functools import partial as fpartial
from json import loads
from discord.ext import commands
from asyncio import BaseEventLoop, get_event_loop

language = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg','ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el','gu', 'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig','id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky','lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi','mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa','ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl','so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk','ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']

color1 = 0x377EF0 #blue
color2 = 0xF8C63D #yellow
color3 = 0x1A8FE3 #aqua
color4 = 0xFF0000 #red
blue = 0x377EF0 #blue
yellow = 0xF8C63D #yellow
aqua = 0x1A8FE3 #aqua
error = 0xFF0000 #red

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