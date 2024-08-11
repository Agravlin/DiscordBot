import discord
import yt_dlp as youtube_dl
import asyncio

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

async def handle_command(client, message: discord.Message) -> str:
    global VOLUME_VALUE

    if message.content.startswith('.play '):
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

    elif message.content.startswith('.volume'):
        if len(message.content) == 7:
            return f'Current Volume is: {VOLUME_VALUE}'
        elif message.content[7:9] == " +" or " -":
            if message.content[8] == "+":
                VOLUME_VALUE += float(message.content[9:])
            else:
                VOLUME_VALUE -= float(message.content[9:])
        VOLUME_VALUE = max(0.0, min(VOLUME_VALUE, 2.0))

    return f"Volume adjusted to {VOLUME_VALUE * 100:.0f}%."