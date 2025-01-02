import discord
import yt_dlp as youtube_dl
import asyncio

# ToDo: Add playlist
# ToDo: Add command menu
# ToDo: Open music with search functionality
# ToDo: Better opening music responses (clickable links etc.)
# ToDo: Disconnect when inactive

VOLUME_VALUE = 0.5

ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': f'-vn -filter:a "volume={VOLUME_VALUE}"'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=VOLUME_VALUE):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
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
    url = message.content.split(' ')[1]
    if message.author.voice:
        channel = message.author.voice.channel
        if not message.guild.voice_client:
            await channel.connect()
        voice_client = message.guild.voice_client

        async with message.channel.typing():
            player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
            player.volume = VOLUME_VALUE
            voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        return f'Now playing: {player.title}'
    else:
        return "You need to be in a voice channel to play music."

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
        voice_client.source.volume = VOLUME_VALUE
        return f"Volume adjusted to {adjustment} (range: 0-100)"
    except ValueError:
        return "Invalid volume adjustment. Please provide a valid number."

async def handle_disconnect(client: discord.Client, message: discord.Message) -> str:
    # If bot is connected to vc
    if message.guild.voice_client: 
        await message.guild.voice_client.disconnect()
        return "Disconnected from the voice channel."
    else:
        return "I'm not connected to any voice channel."