from ..slack import SlackClient
from queue import Queue
from queue import Empty as QueueEmpty
from threading import Thread, Event
from ..util.log import getLogger

_log = getLogger('stream.reader')

class Reader(Thread):
	def __init__(self, token):
		self._client = SlackClient(token)	# create slack client
		self._output = Queue()
		self._exit = Event()
		self._read_int = 1
		super(Reader, self).__init__()
		self.daemon = True					# die on process exit
		self._log = _log.getChild('reader')
		self._id, self._user, = self._retrieve_id()
		self._channel_cache = {}

	def _handle_event(self, event):
		self._log.debug('got event type: %s'%event['type'])
		self._output.put(event)

	def _retrieve_id(self):
		success, resp = self._client.api_call('auth.test')
		print(resp)
		if not success:
			raise Exception('Invalid slack credentials')
		return resp['user_id'], resp['user']

	def _is_public(self, channel):
		if not channel or not isinstance(channel, str):
			return True
		if not channel in self._channel_cache:
			success, resp = self._client.api_call('im.list')
			if success:
				private = [ch['id'] for ch in resp.get('ims', [])]
				self._channel_cache[channel] = not channel in private
		return self._channel_cache[channel]
	
	@property
	def events(self):
		while not self._exit.isSet():
			try:
				event = self._output.get(True, 5)
				if event:
					event['public'] = self._is_public(event.get('channel', None))
					yield event
			except QueueEmpty:
				pass
				
	def run(self):
		delay = 1
		self._log.debug('starting reader, initial backoff %i'%delay)
		while not self._exit.isSet():
			self._log.debug('connecting to slack rtm...')
			if self._client.rtm_connect():
				self._log.debug('connected, waiting for events...')
				delay = 2
				while not self._exit.isSet():
					event = self._client.rtm_read()
					if event:
						event['self'] = event.get('user') == self._id
						if not 'channel' in event.keys():
							event['channel'] = None
						self._handle_event(event)
			else:
				self._log.debug('connection failed')
				if delay <= 16:
					delay += delay
					self._log.debug('increasing backoff to %i'%delay)
				time.sleep(delay)
				

	def join(self):
		self._exit.set()
		self._log.debug('reader exiting...')
		self._client.rtm_close()
		return super(Reader, self).join()	