import asyncio
from functools import partial as fpartial
from json import loads
from itertools import islice
import random
import discord
from async_timeout import timeout
from discord.ext import commands
import settings as s
from datetime import datetime
from requests import get


class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass


def timestamp():
    return datetime.utcnow().timestamp()

def check(url, type, weburl):
    if type == 'YouTube':
        if float(url.split('expire=')[1].split('&')[0]) - 10000 <= timestamp():
            return download(weburl)['url']
        else:
            return url
    else:
        return url

def download(search):
    try:
        data = get('https://akishoudayo-database.herokuapp.com/ytdl/?url={}'.format(search))
        return loads(data.text)
    except:
        return

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


class YTDLSource:
    FFMPEG_OPTIONS = s.ffmpeg_options

    def __init__(self, ctx: commands.Context, settings, *, data: dict):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data
        self.settings = settings
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

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = fpartial(download, search)
        data = await loop.run_in_executor(None, partial)
        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))
        return cls(ctx, cls.FFMPEG_OPTIONS, data=data)


class DurationCalc:
    def __init__(self, endtime):
        self.paused = False
        self.started = False
        self.starttime = 0
        self.pausetime = 0
        self.endtime = endtime

    def start(self):
        self.started = True
        self.starttime = timestamp()

    def now(self):
        if not self.started:
            return
        if not self.paused:
            temp = timestamp() - self.starttime + self.pausetime
            if temp >= self.endtime:
                return self.endtime
            else:
                return temp
        else:
            return self.pausetime

    def pause(self):
        self.paused = True
        self.pausetime = timestamp() - self.starttime

    def resume(self):
        self.paused = False
        self.starttime = timestamp()


class Song:
    # __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
        self._channel = None
        self.duration = DurationCalc(float(source.intduration))
    
    def seteq(self, value, value2):
        self.bass = value
        self.treble = value2

    def setch(self, value):
        self._channel = value

    def create_embed(self, loop='Off', value=None):
        if not value:
            embed = discord.Embed(title='Now Playing', color=discord.Color.blurple(), timestamp=datetime.utcnow())
        else:
            embed = discord.Embed(title='Successfully Added to Queue', color=discord.Color.blurple(), timestamp=datetime.utcnow())
        embed.add_field(name='Title', value='[{0.source.title}]({0.source.url})'.format(self), inline=False)
        if not self.source.artist:
            if self.source.uploader is not None:
                embed.add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self), inline=False)
        else:
            embed.add_field(name='Artist', value='{0.source.artist}'.format(self), inline=False)
        if value:
            embed.add_field(name='Duration', value=self.source.duration, inline=False)
        elif not self.duration.now():
            embed.add_field(name='Duration', value=self.source.duration, inline=False)
        else:
            embed.add_field(name='Duration', value='{} / {}'.format(duration(int(self.duration.now())), self.source.duration), inline=False)
        embed.add_field(name='Codec', value='{0.source.bitrate}'.format(self), inline=False)
        embed.add_field(name='Channel', value='<#{0._channel.channel.id}>'.format(self), inline=False)
        embed.add_field(name='Equalizer', value='Bass : {}dB\nTreble : {}dB'.format(self.bass, self.treble), inline=False)
        embed.set_footer(text='Loop : {1} | Requested by {0.name}#{0.discriminator}'.format(self.requester, loop))
        if self.source.thumbnail is not None:
            embed.set_thumbnail(url=self.source.thumbnail)
        return embed
    
    def getintduration(self):
        try:
            return self.duration.now()
        except:
            return 0

    def queuecheck(self):
        return self.source


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

    def singleloop(self):
        return self._queue[0]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._loooooop = 'Off'
        self._volume = 0.5
        self.bass = 0
        self.treble = 0
        self.starttime = 0
        #-read_ahead_limit 1000k 
        #-hls_allow_cache allowcache 
        self.equalizer = {'opus':{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 50', 'options':'-hls_allow_cache allowcache -vn -af \"firequalizer=gain_entry=\'entry(50,0);entry(100, 0);entry(6300,0);entry(16000,0)\'\"'},'pcm':{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 50', 'options':'-hls_allow_cache allowcache -vn -b:a 200k -af \"firequalizer=gain_entry=\'entry(50,0);entry(100, 0);entry(6300,0);entry(16000,0)\'\"'}}
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: str):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current
    
    def seteq(self, value, value2):
        if value == 'bass':
            self.bass = value2
        if value == 'treble':
            self.treble = value2
        try:
            self.starttime = self.current.getintduration()
        except:
            self.starttime = 0
        self.equalizer = {'opus':{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 50', 'options':'-hls_allow_cache allowcache -ss {0} -vn -af \"firequalizer=gain_entry=\'entry(20,{1});entry(60,{1});entry(100, 0);entry(6300,0);entry(16000,{2})\'\"'.format(self.starttime, self.bass, self.treble)},'pcm':{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 50', 'options':'-hls_allow_cache allowcache -ss {0} -vn -b:a 200k -af \"firequalizer=gain_entry=\'entry(20,{1});entry(60,{1});entry(100, 0);entry(6300,0);entry(16000,{2})\'\"'.format(self.starttime, self.bass, self.treble)}}
        self.current.duration.pause()
        self.current.seteq(self.bass, self.treble)
        self.voice.source = self.player()
        self.current.duration.resume()

    def player(self):
        url = check(self.current.source.stream_url, self.current.source.extractor, self.current.source.url)
        if self.current.source.opus:
            return discord.FFmpegOpusAudio(url, **self.equalizer['opus'])
        else:
            return discord.FFmpegPCMAudio(url, **self.equalizer['pcm'])

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                try:
                    async with timeout(180):
                        if self._loooooop == 'Queue':
                            await self.songs.put(self.played)
                        if self._loooooop == 'Single':
                            self.current = await self.songs.singleloop()
                        else:
                            self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    await self.stop()
                    return
            self.current.duration.start()
            self.played = self.current
            self.current.seteq(self.bass, self.treble)
            self.voice.play(self.player(), after=self.play_next_song)
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))
        if not self._loooooop == 'Single':
            self.next.set()

    def getloop(self):
        return self._loooooop

    def setloop(self, value):
        self._loooooop = value

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
            self.current = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')
        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        try:
            del self.voice_states[ctx.guild.id]
        except:
            await ctx.message.add_reaction('✅')
        ctx.voice_state = self.get_voice_state(ctx)
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.message.add_reaction('✅')
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect', 'dc', 'l'])
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        await ctx.message.add_reaction('✅')
        del self.voice_states[ctx.guild.id]

    @commands.command(name='now', aliases=['current', 'playing', 'n', 'np'])
    async def _now(self, ctx: commands.Context):
        if not ctx.voice_state.getloop():
            await ctx.send(embed=ctx.voice_state.current.create_embed())
        else:
            await ctx.send(embed=ctx.voice_state.current.create_embed(ctx.voice_state.getloop()))

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.current.duration.pause()
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.current.duration.resume()
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop', aliases=[])
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        ctx.voice_state.songs.clear()
        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip', aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            raise commands.CommandError('Nothing to skip song.')

        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        state = ctx.voice_state
        songs = state.songs
        current = state.current
        if not len(songs):
            if not current:
                return await ctx.send('Empty queue.')

        pages = len(songs) // 10
        start = (page - 1) * 10
        end = start + 10
        queue = []
        for n in range(start, end):
            try:
                queue.append('{0}: [{1.source.title}]({1.source.url})'.format(n + 1, songs[n]))
            except:
                pass
        embed = discord.Embed(title='Queue', description='**Now Playing : [{0.title}]({0.url})**\n\n{1}'.format(current.queuecheck(), '\n'.join(queue)), colour=s.color3)
        embed.set_footer(text='Page : {}/{} | Loop : {}'.format(page, pages + 1, state.getloop()))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove', aliases=['delete', 'r', 'rm', 'd'])
    async def _remove(self, ctx: commands.Context, index: int):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop', aliases=['repeat'])
    async def _loop(self, ctx: commands.Context, arg):
        try:
            if arg == 'single':
                ctx.voice_state.setloop('Single')
            elif arg == 'queue':
                ctx.voice_state.setloop('Queue')
            elif arg == 'off':
                ctx.voice_state.setloop('Off')
            else:
                raise Exception('')
            await ctx.message.add_reaction('✅')
        except Exception as e:
            if not e:
                raise commands.CommandError('Mode is wrong\n\n**Mode**\n`single`,`queue`,`off`')
            else:
                raise commands.CommandError('Nothing player in this server.')

    @commands.command(name='bass', aliases=['b'])
    async def _bass(self, ctx: commands.Context, arg: float):
        ctx.voice_state.seteq('bass', arg)
        await ctx.message.add_reaction('✅')

    @commands.command(name='treble', aliases=[])
    async def _treble(self, ctx: commands.Context, arg: float):
        ctx.voice_state.seteq('treble', arg)
        await ctx.message.add_reaction('✅')

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        author = ctx.author.voice.channel
        if not ctx.guild.voice_client:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                self.bot.log(4, e)
                raise commands.CommandError('Not Found Video : `{}`'.format(search))
            else:
                song = Song(source)
                song.setch(author.guild.voice_client)
                song.seteq(ctx.voice_state.bass, ctx.voice_state.treble)
                await ctx.voice_state.songs.put(song)
                await ctx.send(embed=song.create_embed(value=1))
                return

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')


def setup(bot: commands.Bot):
    pass#bot.add_cog(Music(bot))
