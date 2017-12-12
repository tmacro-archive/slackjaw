from ..slack import SlackClient
from ..util.config import config
from ..util.log import getLogger

_log = getLogger('react.room')

slack_client = SlackClient(config.crypto.slack)

def is_public_channel(channel):
	success, resp = slack_client.api_call('channels.info', channel=channel)
	return resp['ok'], resp.get('channel', {}).get('name')

def invite_user(channel, user):
	_log.debug('Inviting %s to %s'%(user, channel))
	return slack_client.api_call('channels.invite', channel=channel, user=user)

def join_room(channel, user, user_token):
	_log.debug('%s is trying to join %s'%(user, channel))
	public, name = is_public_channel(channel)
	_log.debug('%s is %spublic'%(name, 'not ' if public else ''))
	if not public:
		return invite_user(channel, user)
	return slack_client.as_user(user_token).api_call('channels.join', name=name)

def leave_room(channel, user):
	return slack_client.as_user(user).api_call('channels.leave', channel=channel)
