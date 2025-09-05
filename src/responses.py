import discord
import yt_dlp as youtube_dl
import asyncio
from randomness import generate_random_headers
from random import uniform

VOLUME_VALUE = 0.15
music_queues: dict[int, list["YTDLSource"]] = {}

def create_ytdl_options() -> dict:
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'format': 'bestaudio[filesize<10M]',
        'http_headers': generate_random_headers(),
    }

def create_ytdl_instance() -> youtube_dl.YoutubeDL:
    options = create_ytdl_options()
    return youtube_dl.YoutubeDL(options)

async def sleep() -> None:
    await asyncio.sleep(uniform(0.1, 1.0))

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': f'-vn -filter:a "volume={VOLUME_VALUE}"'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=VOLUME_VALUE):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        ytdl = create_ytdl_instance()
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
async def handle_command(client: discord.Client, message: discord.Message) -> str:
    command_content = message.content[1:]
    command = command_content.split()[0] 
    args = command_content.split()[1:]

    match command:
        case "play":
            return await handle_play(client, message, args)
        case "enter":   
            return await handle_enter(client, message)
        case "volume":
            return await handle_volume(client, message, args)
        case "disconnect":
            return await handle_disconnect(client, message)
        case _:
            return "Unknown command. Please try again."

async def handle_play(client: discord.Client, message: discord.Message, args: list[str]) -> str:
    if not args:
        return "Provide a URL or a search query."
    query_or_url = " ".join(args) 

    if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
        return await play_url(client, message, query_or_url)
    else:
        return await play_search(client, message, query_or_url)

async def handle_enter(client: discord.Client, message: discord.Message) -> str:
    await message.author.voice.channel.connect()
    return "I've entered the channel"

async def handle_volume(client: discord.Client, message: discord.Message, args: list[str]) -> str:
    global VOLUME_VALUE
    if not args:
        if message.guild.voice_client and message.guild.voice_client.source:
            current_volume = message.guild.voice_client.source.volume
            return f'Current Volume is: {current_volume:.2f}'
        else:
            return "No audio is currently playing."
    try:
        adjustment = float(args[0]) / 100
        voice_client = message.guild.voice_client

        VOLUME_VALUE = max(0, min(adjustment, 1))
        if voice_client and voice_client.source:
            voice_client.source.volume = VOLUME_VALUE
        return f"Volume adjusted to {adjustment*100} (range: 0-100)"
    except ValueError:
        return "Invalid volume adjustment. Please provide a valid number."

async def handle_disconnect(client: discord.Client, message: discord.Message) -> str:
    # If bot is connected to vc
    if message.guild.voice_client: 
        await message.guild.voice_client.disconnect()
        get_queue(message.guild.id).clear()
        return "Disconnected from the voice channel."
    else:
        return "I'm not connected to any voice channel."
    
async def play_url(client: discord.Client, message: discord.Message, url: str) -> str:
    if not message.author.voice:
        return "You need to be in a voice channel to play music."

    channel = message.author.voice.channel
    if not message.guild.voice_client:
        await channel.connect()
    voice_client = message.guild.voice_client
    async with message.channel.typing():
        try:
            player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
            player.volume = VOLUME_VALUE
            queue = get_queue(message.guild.id)
            if voice_client.is_playing():
                queue.append(player)
                return f"Added to queue: {player.title}"
            voice_client.play(
                player,
                after=lambda e: play_next(message.guild.id, voice_client) if not e else print(f'Player error: {e}'),
            )
        except youtube_dl.DownloadError as e:
            if "format not available" in str(e):
                return "The video is too large to load. Please provide a smaller file."
            else:
                print(e)
                return "An error occurred while processing the URL."

    return f"Now playing: {player.title}"

async def play_search(client: discord.Client, message: discord.Message, query: str) -> str:
    ytdl = create_ytdl_instance()
    await sleep()

    search_results = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)
    )

    if "entries" not in search_results or not search_results["entries"]:
        return "No results found on YouTube."
    url = search_results["entries"][0]["webpage_url"]
    title = search_results["entries"][0]["title"]

    await message.channel.send(f"Found: **{title}**\n{url}")
    return await play_url(client, message, url)

def get_queue(guild_id: int) -> list["YTDLSource"]:
    return music_queues.setdefault(guild_id, [])

def play_next(guild_id: int, voice_client: discord.VoiceClient) -> None:
    queue = get_queue(guild_id)
    if queue:
        next_source = queue.pop(0)
        voice_client.play(
            next_source,
            after=lambda e: play_next(guild_id, voice_client) if not e else print(f'Player error: {e}')
        )
