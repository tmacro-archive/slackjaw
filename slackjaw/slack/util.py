from ..util.config import config
from ..util.log import getLogger
import requests

_log = getLogger('slack.util')

def build_url(method):
	return config.slack.base_url + method

def reqOk(resp):
	if resp.json() and resp.json().get('ok'):
		return True
	return False

def is_jsonable(method):
	return method in JSON_METHODS

def call_method(token, method, **kwargs):
	if is_jsonable(method):
		return call_method_json(token, build_url(method), **kwargs)
	return call_method_urlen(token, build_url(method), **kwargs)

def call_method_urlen(token, url, **kwargs):
	kwargs['token'] = token
	resp = requests.post(url, data = kwargs)
	kwargs.pop('token') # DO NOT REMOVE!! Otherwise tokens will leak into logs
	_log.debug('<%s> %s -> %s'%(url, kwargs, resp.json()))
	return reqOk(resp), resp.json()

def call_method_json(token, url, **kwargs):
	headers = {'Authorization': 'Bearer %s'%token}
	resp = requests.post(url, json = kwargs, headers = headers)
	_log.debug('<%s> %s -> %s'%(url, kwargs, resp.json()))
	return reqOk(resp), resp.json()

JSON_METHODS = [
	'api.test',
	'auth.test',
	'channels.archive',
	'channels.create',
	'channels.invite',
	'channels.join',
	'channels.kick',
	'channels.leave',
	'channels.mark',
	'channels.rename',
	'channels.setPurpose',
	'channels.setTopic',
	'channels.unarchive',
	'chat.delete',
	'chat.meMessage',
	'chat.postEphemeral',
	'chat.postMessage',
	'chat.unfurl',
	'chat.update',
	'conversations.archive',
	'conversations.close',
	'conversations.create',
	'conversations.invite',
	'conversations.join',
	'conversations.kick',
	'conversations.leave',
	'conversations.open',
	'conversations.rename',
	'conversations.setPurpose',
	'conversations.setTopic',
	'conversations.unarchive',
	'dialog.open',
	'dnd.endDnd',
	'dnd.endSnooze',
	'files.comments.add',
	'files.comments.delete',
	'files.comments.edit',
	'files.delete',
	'files.revokePublicURL',
	'files.sharedPublicURL',
	'groups.archive',
	'groups.create',
	'groups.invite',
	'groups.kick',
	'groups.leave',
	'groups.mark',
	'groups.open',
	'groups.rename',
	'groups.setPurpose',
	'groups.setTopic',
	'groups.unarchive',
	'im.close',
	'im.mark',
	'im.open',
	'mpim.close',
	'mpim.mark',
	'mpim.open',
	'pins.add',
	'pins.remove',
	'reactions.add',
	'reactions.remove',
	'reminders.add',
	'reminders.complete',
	'reminders.delete',
	'stars.add',
	'stars.remove',
	'usergroups.create',
	'usergroups.disable',
	'usergroups.enable',
	'usergroups.update',
	'usergroups.users.update',
	'users.profile.set',
	'users.setActive',
	'users.setPresence',
]
