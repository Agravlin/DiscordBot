import discord
import yt_dlp as youtube_dl
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
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
    if message.content.startswith('.play '):
        url = message.content.split(' ')[1]
        if message.author.voice:
            channel = message.author.voice.channel
            if not message.guild.voice_client:
                await channel.connect()
            voice_client = message.guild.voice_client

            async with message.channel.typing():
                player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
                voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            return f'Now playing: {player.title}'
        else:
            return "You need to be in a voice channel to play music."

    # Add more command handling logic here
    return None
