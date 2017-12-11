from ..slack import SlackClient
from ..util.config import config

slack_client = SlackClient(config.crypto.slack)

def emoji_react(channel, ts, emoji, token):
    return slack_client.as_user(token).api_call('reactions.add', channel=channel, timestamp=ts, name=emoji)

def duplicate_reaction(event, token):
    return emoji_react(event['item']['channel'], event['item']['ts'], event['reaction'], token)
