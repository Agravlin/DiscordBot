import discord
import responses
from config import DISCORD_TOKEN


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')

    @client.event
    async def on_message(message: discord.Message) -> None:
        # Prevent recursive messages
        if message.author == client.user:
            return
            
        # Print the content
        print(f'{message.author} wrote {message.content}')

        # Starting letter
        if message.content.startswith('.'):
            await message.channel.send('Hello!')

    client.run(token=DISCORD_TOKEN)
