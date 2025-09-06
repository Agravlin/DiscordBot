import discord
import responses
from config import DISCORD_TOKEN
import time
import asyncio

MESSAGE_PREFIX = "-"
last_activity = time.time()
INACTIVITY_TIMEOUT = 300  # 5 minutes

def run_discord_bot() -> None:
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        print(f'Logged in as {client.user}')
        client.loop.create_task(check_inactivity(client))     

    @client.event
    async def on_message(message: discord.Message) -> None:
        global last_activity
        # Prevent recursive messages
        if message.author == client.user:
            return
            
        # Print the content
        print(f'{message.author} wrote {message.content}')
        last_activity = time.time()
        # Starting letter
        if message.content.startswith(MESSAGE_PREFIX):
            response = await responses.handle_command(client, message)
            if response:
                await message.channel.send(response)

    async def check_inactivity(client: discord.Client) -> None:
        await client.wait_until_ready()
        while not client.is_closed():
            current_time = time.time()
            for vc in client.voice_clients:
                guild_queue_empty = not responses.get_queue(vc.guild.id)
                if (
                    vc.is_connected()
                    and not vc.is_playing()
                    and guild_queue_empty
                    and (current_time - last_activity) > INACTIVITY_TIMEOUT
                ):
                    await vc.disconnect()
                    responses.get_queue(vc.guild.id).clear()
                    print("Disconnected due to inactivity.")
            await asyncio.sleep(60)
    client.run(token=DISCORD_TOKEN)
