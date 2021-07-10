import os
import requests
import discord
from discord.ext import commands
from keep_alive import keep_alive

redirect_uri = 'http://localhost'
twitch_token_auth_url = 'https://id.twitch.tv/oauth2/token'
twitch_users_api = 'https://api.twitch.tv/helix/users'
twitch_validate_api = 'https://id.twitch.tv/oauth2/validate'
twitch_emote_api = 'https://api.twitch.tv/helix/chat/emotes'
bttv_user_api = 'https://api.betterttv.net/3/cached/users/twitch/'
ffz_user_api = 'https://api.frankerfacez.com/v1/room/id/'
twitch_global_emote_api = 'https://api.twitch.tv/helix/chat/emotes/global'
bttv_global_emotes = 'https://api.betterttv.net/3/cached/emotes/global'
ffz_global_emote_api = 'https://api.frankerfacez.com/v1/set/global'

twitch_animated_emote_url = lambda emote_id: 'https://static-cdn.jtvnw.net/emoticons/v2/' + emote_id + '/default/dark/3.0'
bttv_emote_url = lambda emote_id: 'https://cdn.betterttv.net/emote/' + emote_id + '/3x'

class BotClient(commands.Bot):

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
            'grant_type': 'client_credentials'
        }
        response = requests.post(twitch_token_auth_url, data=auth_header)
        response_dict = response.json()
        self.access_token = response_dict['access_token']
        self.token_header = {
            'Authorization': 'Bearer ' + self.access_token,
            'Client-Id': self.client_id
        }
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
        user_param = {'login': channel_name}
        response = requests.get(twitch_users_api,
                                params=user_param,
                                headers=self.token_header)
        response_dict = response.json()['data'][0]
        channel_id = response_dict['id']
        return channel_id

    def get_twitch_emoteURL(self, channel_id, emote_name):
        """Makes a call to Twitch API to get a channel's emote from a specific emote name

        Param channel_id: The unique identifier of the channel (String)
        Param emote_name: The name of the emote (String)
        
        Returns: URL to display requested emote (String)
        """
        param = {'broadcaster_id': channel_id}
        response = requests.get(twitch_emote_api,
                                params=param,
                                headers=self.token_header)
        response_list = response.json()['data']
        for dicts in response_list:
            if (dicts['name'].lower() == emote_name.lower()):
                if (dicts['id'].startswith('emotesv2_')):
                    url = twitch_animated_emote_url(dicts['id'])
                else:
                    url = dicts['images']['url_4x']
                return url

        return None

    def get_bttv_emoteURL(self, channel_id, emote_name):
        """Makes a call to BetterTTV API to get a channel's emote from a specific emote name

        Param channel_id: The unique identifier of the channel (String)
        Param emote_name: The name of the emote (String)
        
        Returns: URL to display requested emote (String)
        """
        response = requests.get(bttv_user_api + channel_id)
        channel_emotes = response.json()['channelEmotes']
        shared_emotes = response.json()['sharedEmotes']
        for emotes in channel_emotes:
            if (emotes['code'].lower() == emote_name.lower()):
                url = bttv_emote_url(emotes['id'])
                if (emotes['imageType'] == 'gif'):
                    url += '.gif'
                return url
        for emotes in shared_emotes:
            if (emotes['code'].lower() == emote_name.lower()):
                url = bttv_emote_url(emotes['id'])
                if (emotes['imageType'] == 'gif'):
                    url += '.gif'
                return url
        return None

    def get_ffz_emoteURL(self, channel_id, emote_name):
        """Makes a call to FrankerFaceZ API to get a channel's emote from a specific emote name

        Param channel_id: The unique identifier of the channel (String)
        Param emote_name: The name of the emote (String)
        
        Returns: URL to display requested emote (String)
        """
        response = requests.get(ffz_user_api + channel_id)
        response_json = response.json()
        for sets in response_json['sets'].values():
          for emotes in sets['emoticons']:
            if (emotes['name'].lower() == emote_name.lower()):
                url = 'https:' + emotes['urls'][max(emotes['urls'], key=int)]
                return url
        return None

    def get_twitch_global_emoteURL(self, emote_name):
      """Makes a call to Twitch API to get a global emote from an emote name

      Param emote_name: The name of the emote (String)
      
      Returns: URL to display requested emote (String)
      """
      response = requests.get(twitch_global_emote_api,
                              headers=self.token_header)
      response_list = response.json()['data']
      for dicts in response_list:
          if (dicts['name'].lower() == emote_name.lower()):
              if (dicts['id'].startswith('emotesv2_')):
                  url = twitch_animated_emote_url(dicts['id'])
              else:
                  url = dicts['images']['url_4x']
              return url
      return None

    def get_bttv_global_emoteURL(self, emote_name):
      """Makes a call to BetterTTV API to get a global emote from an emote name

      Param emote_name: The name of the emote (String)
      
      Returns: URL to display requested emote (String)
      """
      emote_set = requests.get(bttv_global_emotes).json()
      for emotes in emote_set:
        if (emotes['code'].lower() == emote_name.lower()):
          return bttv_emote_url(emotes['id'])
      return None

    def get_ffz_global_emoteURL(self, emote_name):
      """Makes a call to FrankerFaceZ API to get a global emote from an emote name

      Param emote_name: The name of the emote (String)
    
      Returns: URL to display requested emote (String)
      """
      response = requests.get(ffz_global_emote_api)
      response_json = response.json()
      for sets in response_json['sets'].values():
        for emotes in sets['emoticons']:
          if (emotes['name'].lower() == emote_name.lower()):
              url = 'https:' + emotes['urls'][max(emotes['urls'], key=int)]
              return url
      return None

cmd_prefix = '^'
client = BotClient(command_prefix=cmd_prefix, help_command=None)

@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))

@client.event
async def on_connect():
  act = discord.Streaming(name="Do ^help", url="https://twitch.tv/dextinfire")
  await client.change_presence(activity=act)
  client.get_twitch_app_access_token()

@client.command()
async def emote(ctx, channel_name, emote_name):
    client.validate_access_token()
    print("Channel Name: " + channel_name + " Emote Name: " + emote_name)
    channel_id = client.get_channelID(channel_name)
    print("Channel ID: " + channel_id)
    emote_URL = client.get_twitch_emoteURL(channel_id, emote_name)
    if(emote_URL == None):
        emote_URL = client.get_bttv_emoteURL(channel_id, emote_name)
    if(emote_URL == None):
        emote_URL = client.get_ffz_emoteURL(channel_id, emote_name)
    response_string = emote_URL if emote_URL else "Emote cannot be found"
    await ctx.send(response_string)

@client.command(aliases=['global'])
async def _global(ctx, emote_name):
    client.validate_access_token()
    print("Emote Name: " + emote_name)
    emote_URL = client.get_twitch_global_emoteURL(emote_name)
    if(emote_URL == None):
        emote_URL = client.get_bttv_global_emoteURL(emote_name)
    if(emote_URL == None):
        emote_URL = client.get_ffz_global_emoteURL(emote_name)
    response_string = emote_URL if emote_URL else "Emote cannot be found"
    await ctx.send(response_string)

@client.command()
async def help(ctx):
    await ctx.send("``` HELP \n^emote <Twitch Channel> <Emote> Grab an emote for a specific Twitch channel and send it as an image. Supports Twitch sub emotes, BTTV, and FFZ.```")

@emote.error
async def emote_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = "Requires both channel name and emote name (in that order)"
    else:
        message = "Unknown error occured with command!"
        raise error

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)

@_global.error
async def global_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = "Missing emote name"
    else:
        message = "Unknown error occured with command!"
        raise error

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)

keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
