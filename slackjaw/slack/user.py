from ..util.config import config
from ..util.log import getLogger
# from .slack import SlackClient
from .util import call_method

_log = getLogger('slack.user')


class SlackUser:
	def __init__(self, token):
		self._token = token
		self._id = None
		self._channels = {}

	def _call(self, method, **kwargs):
		return call_method(self._token, method, **kwargs)

	def _is_public_channel(self, channel):
		if not self._channels.get(channel):
			ok, resp = self._call('channels.info', channel = channel)
			self._channels[channel] = (ok, resp.get('channel', {}).get('name'))
		return self._channels[channel]

	def send(self, msg, channel = None, emoji = None):
		ok, resp = self._call('chat.postMessage', channel = channel, text = msg)
		if ok and emoji:
			return self.react(resp['channel'], resp['ts'], emoji)
		return resp
	
	def join(self, channel):
		public, name = self._is_public_channel(channel)
		if not public:
			return False
		ok, resp = self._call('channels.join', name = name)
		return ok

	def invite(self, channel, user = None):
		ok, resp = self._call('groups.invite', channel = channel, user = user)
		return ok

	def leave(self, channel):
		public, name = self._is_public_channel(channel)
		if public:		
			ok, resp = self._call('channels.leave', channel = channel)
		else:
			ok, resp = self._call('groups.leave', channel = channel)
		return ok

	def react(self, channel, timestamp, emoji):
		ok, resp = self._call('reactions.add', channel = channel, timestamp = timestamp,  name = emoji)
		return ok
	
	def messages(self, user = None, channel = None):
		pass
		
	@property
	def chat(self):
		pass
	
	def channels(self, public = True, private = True):
		channels = []
		if public:
			ok, resp = self._call('channels.list', exclude_archived = True, exclude_members = True)	
			if ok:
				for c in resp.get('channels', []):
					channels.append((c['id'], c['is_private']))
		if private:
			ok, resp = self._call('groups.list', exclude_archived = True, exclude_members = True)
			if ok:
				for c in resp.get('groups', []):
					channels.append((c['id'], True))
		return channels

	def _get_profile(self, key = None):
		ok, resp = self._call('users.profile.get')
		if ok:
			profile = resp.get('profile')
			if key:
				return profile.get(key)
			return profile
		return None

	def _set_profile(self, **kwargs):
		ok, resp = self._call('users.profile.set', profile = kwargs)
		return resp.get('profile') if ok else None
	
	@property
	def token(self):
		return self._token
		
	@property
	def id(self):
		if not self._id:
			ok, resp = self._call('auth.test')
			if ok:
				self._id = resp.get('user_id')
		return self._id
		
	@property
	def name(self):
		return self._get_profile('display_name_normalized')

	@name.setter
	def name(self, value):
		return self._set_profile(display_name = value)

	@property
	def emoji(self):
		return self._get_profile('status_emoji')
	
	@emoji.setter
	def emoji(self, value):
		return self._set_profile(status_emoji = ':%s:'%value)
		
	@property
	def status(self):
		return self._get_profile('status_text')

	@status.setter
	def status(self, value):
		return self._set_profile(status_text = value)
