from ..slack import SlackClient
from ..util.config import config

slack_client = SlackClient(config.crypto.slack)

def is_public_channel(channel):
    success, resp = slack_client.api_call('channels.info', channel=channel)
    return resp['ok'], resp.get('channel', {}).get('name')

def invite_user(channel, user):
    print(channel)
    return slack_client.api_call('channels.invite', channel=channel, user=user)

def join_room(channel, user, user_token):
    public, name = is_public_channel(channel)
    if not public:
        return invite_user(channel, user)
    return slack_client.as_user(user_token).api_call('channels.join', name=name)

def leave_room(channel, user):
    return slack_client.as_user(user).api_call('channels.leave', channel=channel)      
