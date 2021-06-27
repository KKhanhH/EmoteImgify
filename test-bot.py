import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()

cmdPrefix = '^'

redirect_uri='http://localhost'
twitch_token_auth_url='https://id.twitch.tv/oauth2/token'
twitch_users_api='https://api.twitch.tv/helix/users'
twitch_validate_api='https://id.twitch.tv/oauth2/validate'


client = discord.Client()

def validate_access_token(access_token):
    """Validates that the app access token has not yet expired,
    if access token has expired, grabs a new one

    Returns: None
    """
    token_header = {'Authorization': 'OAuth ' + access_token}
    response = requests.get(twitch_validate_api, headers=token_header)
    if response.ok:
        return access_token
    get_twitch_app_access_token()


def get_twitch_app_access_token():
    """Makes a call to Twitch authentication API to get an app access token
    Uses client id and client secret from hidden token environment variables

    Returns:
    String: The app access token from the API response
    """
    auth_header = {
        'client_id': os.getenv("TWITCH_CLIENT_ID"),
        'client_secret': os.getenv("TWITCH_CLIENT_SECRET"),
        'grant_type':'client_credentials'
    }
    response = requests.post(twitch_token_auth_url, data=auth_header)
    response_dict = response.json()
    access_token = response_dict['access_token']
    print(response_dict)
    return access_token

def get_channelID(access_token, channel_name):
    """Makes a call to Twitch API to get an user's channel ID from their name

    Param channel_name: The channel name of the user to lookup (String)
    
    Returns: The app access token from the API response (String)
    """
    user_param={'login': channel_name}
    token_header = {'Authorization': 'Bearer ' + access_token}
    response = requests.post(twitch_token_auth_url, params=user_param, headers=token_header)
    response_dict = response.json()
    channel_id = response_dict['id']
    return channel_id

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

    if (message.content.startswith(cmdPrefix + 'accesstokentest')):
        access_token = get_twitch_app_access_token()
        await message.channel.send('Printed!')

client.run(os.getenv("DISCORD_TOKEN"))
