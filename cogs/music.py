import asyncio
import datetime as dt
import random
import re
import typing as t
import requests
from json import loads
from os import getenv
import discord
import wavelink
from discord.ext import commands
import settings as st

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
LYRICS_URL = "https://some-random-api.ml/lyrics?title="
HZ_BANDS = (20, 40, 60, 80, 100, 14000, 16000)
TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class AlreadyConnectedToChannel(commands.CommandError):
    pass
class NoVoiceChannel(commands.CommandError):
    pass
class QueueIsEmpty(commands.CommandError):
    pass
class NoTracksFound(commands.CommandError):
    pass
class PlayerIsAlreadyPaused(commands.CommandError):
    pass
class PlayerIsAlreadyResumed(commands.CommandError):
    pass
class NoMoreTracks(commands.CommandError):
    pass
class NoPreviousTracks(commands.CommandError):
    pass
class InvalidRepeatMode(commands.CommandError):
    pass
class VolumeTooLow(commands.CommandError):
    pass
class VolumeTooHigh(commands.CommandError):
    pass
class MaxVolume(commands.CommandError):
    pass
class MinVolume(commands.CommandError):
    pass
class NoLyricsFound(commands.CommandError):
    pass
class InvalidEQPreset(commands.CommandError):
    pass
class NonExistentEQBand(commands.CommandError):
    pass
class EQGainOutOfBounds(commands.CommandError):
    pass
class InvalidTimeString(commands.CommandError):
    pass
class ZeroConnectedNodes(commands.CommandError):
    pass

def download(search):
    try:
        data = requests.get('https://akishoudayo-database.herokuapp.com/ytdl?url={}'.format(search))
        return loads(data.text)
    except:
        return

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = 0

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == 2:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == "off":
            self.repeat_mode = 0
        elif mode == "single":
            self.repeat_mode = 1
        elif mode == "queue":
            self.repeat_mode = 2

    def empty(self):
        self._queue.clear()
        self.position = 0


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()
        self.eq_levels = [0.] * 15

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id, self_deaf=True)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks, message):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await message.edit(content=f":white_check_mark: **Added `{tracks[0].title}` to the queue.**")
        else:
            if (track := await self.choose_track(ctx, tracks, message)) is not None:
                self.queue.add(track)
                await message.edit(content=f":white_check_mark: **Added `{track.title}` to the queue.**", embed=None)
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks, msg):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await msg.edit(content=None, embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
        else:
            await msg.clear_reactions()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        self.bot.log(1, f"Wavelink : node-{node.identifier} is ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == 1:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(":x: **Music commands are not available in direct messages.**")
            self.bot.data['smessages'] += 1
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        for node in self.bot.data['nodes']:
            self.bot.nodes = self.wavelink
            try:
                await self.wavelink.initiate_node(host=node['host'], port=node['port'], rest_uri='http://{}:{}'.format(node['host'], node['port']), password=self.bot.data['password'], identifier=node['name'], region=node['region'], heartbeat=5)
            except Exception as e:
                self.bot.log(2, e)


    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join", "summon", "j"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f":white_check_mark: **Connected to `{channel.name}`.**")
        self.bot.data['smessages'] += 1

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send(":x: **Already connected to a voice channel.**")
            self.bot.data['smessages'] += 1
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send(":x: **No suitable voice channel was provided.**")
            self.bot.data['smessages'] += 1

    @commands.command(name="disconnect", aliases=["leave", "dc", "l", "d"])
    async def disconnect_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send(":white_check_mark: **Disconnected.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="play", aliases=["p"])
    async def play_command(self, ctx, *, query: t.Optional[str]):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send(":arrow_forward: **Playback resumed.**")
            self.bot.data['smessages'] += 1

        else:
            ms = await ctx.send(':arrows_counterclockwise: **Searching...**')
            self.bot.data['smessages'] += 1
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"
            query = await self.wavelink.get_tracks(query)
            if isinstance(query, wavelink.TrackPlaylist):
                await player.add_tracks(ctx, query, ms)
            else:
                await player.add_tracks(ctx, [query[0]], ms)

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(":x: **Queue is empty. Player won\'t be playing.**")
            self.bot.data['smessages'] += 1
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send(":x: **Not connected to any voice channel.**")
            self.bot.data['smessages'] += 1



    @commands.command(name="search")
    async def search_command(self, ctx, *, query: t.Optional[str]):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send(":arrow_forward: **Playback resumed.**")
            self.bot.data['smessages'] += 1

        else:
            ms = await ctx.send(':arrows_counterclockwise: Searching...')
            self.bot.data['smessages'] += 1
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"
            await player.add_tracks(ctx, await self.wavelink.get_tracks(query), ms)

    @search_command.error
    async def search_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(":x: **Queue is empty. Player won\'t be playing.**")
            self.bot.data['smessages'] += 1
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send(":x: **Not connected to any voice channel.**")
            self.bot.data['smessages'] += 1

    @commands.command(name="pause")
    async def pause_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send(":pause_button: **Playback paused.**")
        self.bot.data['smessages'] += 1

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send(":x: **Already paused.**")
            self.bot.data['smessages'] += 1

    @commands.command(name="resume")
    async def resume_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not player.is_paused:
            raise PlayerIsAlreadyResumed

        await player.set_pause(False)
        await ctx.send(":arrow_forward: **Playback resumed.**")
        self.bot.data['smessages'] += 1

    @resume_command.error
    async def resume_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyResumed):
            await ctx.send(":x: **Already resumed.**")
            self.bot.data['smessages'] += 1


    @commands.command(name="stop")
    async def stop_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send(":stop_button: **Playback stopped.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="next", aliases=["skip", "s"])
    async def next_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.is_paused:
            if player.queue.upcoming:
                pass
            else:
                await ctx.send(":stop_button: **Queue is empty. Player stopped.**")
                self.bot.data['smessages'] += 1
                await player.stop()
                return

        await player.stop()
        await ctx.send(":track_next: **Playing next track in queue**")
        self.bot.data['smessages'] += 1

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            raise commands.CommandError("This could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoMoreTracks):
            raise commands.CommandError("There are no more tracks in the queue.")

    @commands.command(name="previous")
    async def previous_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send(":track_previous: **Playing previous track in queue**")
        self.bot.data['smessages'] += 1

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            raise commands.CommandError("This could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoPreviousTracks):
            raise commands.CommandError("There are no previous tracks in the queue.")

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send(":twisted_rightwards_arrows: **Queue shuffled**")
        self.bot.data['smessages'] += 1

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            raise commands.CommandError("The queue could not be shuffled as it is currently empty.")

    @commands.command(name="repeat", aliases=['loop'])
    async def repeat_command(self, ctx, mode: str):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        if mode not in ("off", "single", "queue"):
            raise commands.CommandError("Modes : `off`/`single`/`queue`")

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        if mode == 'single':
            await ctx.send(f":repeat_one: **Successfully repeat mode set to `single`.**")
        if mode == 'queue':
            await ctx.send(f":repeat: **Successfully repeat mode set to `queue`.**")
        if mode == 'off':
            await ctx.send(f":arrow_forward: **Successfully repeat mode set to `off`.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="queue", aliases=["q"])
    async def queue_command(self, ctx, page: int = 1):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        if not page:
            raise commands.CommandError("Invaild page.")
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise commands.CommandError("The queue is currently empty.")
        if not page * 10 <= ((len(player.queue.upcoming)/10)+1) * 10:
            raise commands.CommandError("Invaild page.")
        queues = player.queue.upcoming
        queue = []
        for n in range(page*10-10, page*10):
            try:
                queue.append('{} : [{}]({})'.format(n+1, queues[n].title, queues[n].uri))
            except:
                break
        if not player.queue.upcoming:
            embed = discord.Embed(title="Queue",
                                  description="**Now Playing** : [{}]({})".format(player.queue.current_track.title, player.queue.current_track.uri),
                                  colour=ctx.author.colour,
                                  timestamp=dt.datetime.utcnow())
        else:
            embed = discord.Embed(title="Queue",
                                  description="**Now Playing** : [{}]({})\n\n{}".format(player.queue.current_track.title, player.queue.current_track.uri, '\n'.join(queue)),
                                  colour=ctx.author.colour,
                                  timestamp=dt.datetime.utcnow())
        embed.set_footer(text=f"Page {page}/{int(len(player.queue.upcoming)/10)+1}")
        await ctx.send(embed=embed)
        self.bot.data['smessages'] += 1

    @commands.command(name="remove", aliases=["r"])
    async def remove_command(self, ctx, value: int):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise commands.CommandError("The queue is currently empty.")
        try:
            if value == 0:
                await ctx.send(':x: **Invaild value.**')
            else:
                del player.queue._queue[value]
            await ctx.send(':white_check_mark: **Successfully Deleted.**')
        except:
            await ctx.send(':x: **Invaild value.**')
        self.bot.data['smessages'] += 1

    # Requests -----------------------------------------------------------------

    @commands.group(name="volume", aliases=["vol"], invoke_without_command=True)
    async def volume_group(self, ctx, volume: int):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if volume < 0:
            raise commands.CommandError("The volume must be 0% or above.")

        if volume > 150:
            raise commands.CommandError("The volume must be 150% or below.")

        await player.set_volume(volume)
        await ctx.send(f":white_check_mark: **Successfully changed volume to {volume:,}%**")
        self.bot.data['smessages'] += 1

    @volume_group.command(name="up")
    async def volume_up_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.volume == 150:
            raise commands.CommandError("The player is already at max volume.")

        await player.set_volume(value := min(player.volume + 10, 150))
        await ctx.send(f":white_check_mark: Volume set to {value:,}%")
        self.bot.data['smessages'] += 1

    @volume_group.command(name="down")
    async def volume_down_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.volume == 0:
            raise commands.CommandError("The player is already at min volume.")

        await player.set_volume(value := max(0, player.volume - 10))
        await ctx.send(f":white_check_mark: **Volume set to {value:,}%**")
        self.bot.data['smessages'] += 1

    @commands.command(name="eq")
    async def eq_command(self, ctx, preset: str):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        eq = getattr(wavelink.eqs.Equalizer, preset, None)
        if not eq:
            raise commands.CommandError("Presets : `flat`,`boost`,`metal`,`piano`")

        await player.set_eq(eq())
        await ctx.send(f":white_check_mark: **Equaliser adjusted to the `{preset}` preset.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="adveq", aliases=["aeq"])
    async def adveq_command(self, ctx, band: int, gain: float):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not 1 <= band <= 15 and band not in HZ_BANDS:
            raise commands.CommandError("This is a 15 band equaliser -- the band number should be between 1 and 15, or one of the following\
                                        frequencies: " + ", ".join(str(b) for b in HZ_BANDS))

        if band > 15:
            band = HZ_BANDS.index(band) + 1

        if abs(gain) > 10:
            raise commands.CommandError("The EQ gain for any band should be between 10 dB and -10 dB.")

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(levels=[(i, gain) for i, gain in enumerate(player.eq_levels)])
        await player.set_eq(eq)
        await ctx.send(":white_check_mark: **Equaliser adjusted.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="bass", aliases=["b"])
    async def bass_command(self, ctx, gain: float):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        band = 20

        if band > 15:
            band = HZ_BANDS.index(band) + 1

        if abs(gain) > 10:
            raise commands.CommandError("The EQ gain for any band should be between 10 dB and -10 dB.")

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(levels=[(i, gain) for i, gain in enumerate(player.eq_levels)])
        await player.set_eq(eq)
        await ctx.send(f":white_check_mark: **Successfully bassboost set to {gain}db.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="treble", aliases=[])
    async def treble_command(self, ctx, gain: float):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        band = 16000

        if band > 15:
            band = HZ_BANDS.index(band) + 1

        if abs(gain) > 10:
            raise commands.CommandError("The EQ gain for any band should be between 10 dB and -10 dB.")

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(levels=[(i, gain) for i, gain in enumerate(player.eq_levels)])
        await player.set_eq(eq)
        await ctx.send(f":white_check_mark: **Successfully trebleboost set to {gain}db.**")
        self.bot.data['smessages'] += 1

    @commands.command(name="playing", aliases=["np", "n"])
    async def playing_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if not player.is_playing:
            raise commands.CommandError("There is no track currently playing.")
        print(player.queue.current_track.info)
        embed = discord.Embed(title="Now Playing",colour=ctx.author.colour,timestamp=dt.datetime.utcnow())
        #embed.set_author(name="Playback Information")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Title", value=f'[{player.queue.current_track.title}]({player.queue.current_track.uri})', inline=False)
        embed.add_field(name="Uploader", value=player.queue.current_track.author, inline=False)
        try:
            embed.set_thumbnail(url=f'https://img.youtube.com/vi/{player.queue.current_track.ytid}/hqdefault.jpg')
        except:
            pass
        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=False
        )

        await ctx.send(embed=embed)
        self.bot.data['smessages'] += 1

    @commands.command(name="skipto", aliases=["playindex"])
    async def skipto_command(self, ctx, index: int):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise commands.CommandError("There are no tracks in the queue.")

        if not 0 <= index <= player.queue.length:
            raise commands.CommandError("That index is out of the bounds of the queue.")

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f":white_check_mark: **Playing track in position {index}.**")
        self.bot.data['smessages'] += 1

    aa = '''@commands.command(name="restart")
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Track restarted.")

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")'''

    @commands.command(name="seek")
    async def seek_command(self, ctx, position: str):
        if not ctx.author.voice:
            await ctx.send(':x: **You are not connected to any voice channel.**')
            return
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise commands.CommandError("There are no tracks in the queue.")

        if not (match := re.match(TIME_REGEX, position)):
            raise commands.CommandError("Invalid time string.")

        if match.group(3):
            secs = (int(match.group(1)) * 60) + (int(match.group(3)))
        else:
            secs = int(match.group(1))

        await player.seek(secs * 1000)
        await ctx.send(f":white_check_mark: **Successfully seeked to {position}.**")
        self.bot.data['smessages'] += 1


def setup(bot):
    bot.add_cog(Music(bot))