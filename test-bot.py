import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()

redirect_uri='http://localhost'
twitch_token_auth_url='https://id.twitch.tv/oauth2/token'
twitch_users_api='https://api.twitch.tv/helix/users'
twitch_validate_api='https://id.twitch.tv/oauth2/validate'
twitch_emote_api='https://api.twitch.tv/helix/chat/emotes'

class BotClient(discord.Client):

    cmdPrefix = '^'
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    
    def get_twitch_app_access_token(self):
        """Makes a call to Twitch authentication API to get an app access token
        Uses client id and client secret from hidden token environment variables
        Sets instance variable of access_token to the app access token from the API response

        Returns: Boolean indicating whether the API request failed or succeeded
        
        """
        auth_header = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type':'client_credentials'
        }
        response = requests.post(twitch_token_auth_url, data=auth_header)
        response_dict = response.json()
        self.access_token = response_dict['access_token']
        self.token_header = {'Authorization': 'Bearer ' + self.access_token, 'Client-Id': self.client_id}
        print(response_dict)
        return response.ok

    def validate_access_token(self):
        """Validates that the app access token has not yet expired,
        if access token has expired, grabs a new one
        
        Returns: None
        """
        token_header = {'Authorization': 'OAuth ' + self.access_token}
        response = requests.get(twitch_validate_api, headers=token_header)
        if response.ok:
            return
        self.get_twitch_app_access_token()

    def get_channelID(self, channel_name):
        """Makes a call to Twitch API to get an user's channel ID from their name

        Param channel_name: The channel name of the user to lookup (String)
        
        Returns: The app access token from the API response (String)
        """
        self.validate_access_token()
        user_param={'login': channel_name}
        response = requests.get(twitch_users_api, params=user_param, headers=token_header)
        response_dict = response.json()['data'][0]
        channel_id = response_dict['id']
        return channel_id

    def get_emoteURL(self, channel_id, emote_name):
        """Makes a call to Twitch API to get a channel's emote from a specific emote name

        Param channel_id: The unique identifier of the channel (String)
        Param emote_name: The name of the emote (String)
        
        Returns: URL to display requested emote (String)
        """
        self.validate_access_token()
        param={'broadcaster_id': channel_id}
        response = requests.get(twitch_emote_api, params=param, headers=token_header)
        response_list = response.json()['data']
        for dicts in response_list:
            if(dicts['name'] == emote_name):
                return dicts['images']['url_4x']
        return None

    
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.get_twitch_app_access_token()

    async def on_message(self, message):
        # Ignore messages coming from our own client
        if (message.author == self.user):
            return

        if (message.content.startswith(cmdPrefix + 'hello')):
            await message.channel.send('Hello World!')

        if (message.content.startswith(cmdPrefix + 'accesstokentest')):
            get_twitch_app_access_token()
            await message.channel.send('Printed!')

client = BotClient()
client.run(os.getenv("DISCORD_TOKEN"))
