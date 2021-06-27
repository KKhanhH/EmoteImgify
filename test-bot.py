import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()

cmdPrefix = '^'

redirect_uri='http://localhost'

client = discord.Client()

@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))

@client.event
async def on_message(message):
    # Ignore messages coming from our own client
    if (message.author == client.user):
        return

    if (message.content.startswith(cmdPrefix + 'hello')):
        await message.channel.send('Hello World!')


client.run(os.getenv("DISCORD_TOKEN"))
