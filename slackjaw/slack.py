import websocket
import requests
from .util.config import config
from .util.log import getLogger
from queue import Queue, Empty
from threading import Event, Thread
import json

_log = getLogger('slack')

def build_url(method):
	return 'https://slack.com/api/' + method

def reqOk(resp):
	if resp.json() and resp.json().get('ok'):
		return True
	return False

def call_method(token, method, **kwargs):
	kwargs['token'] = token
	resp = requests.post(build_url(method), data = kwargs)
	print(resp.json())
	return reqOk(resp), resp.json()

class WSocket(Thread):
	def __init__(self, ws, connected):
		self._connected = connected
		self._ws = ws
		super().__init__()

	def start(self):
		self._connected.set()
		super().start()
	
	def run(self):
		self._ws.run_forever()
	
	def join(self):
		self._ws.close()
		super().join()

class SlackClient:
	def __init__(self, token):
		self._token = token
		self._ws_url = None
		self._ws = None
		self._output = Queue()
		self._connected = Event()

	def api_call(self, method, **kwargs):
		return call_method(self._token, method, **kwargs)

	def rtm_connect(self):
		_log.debug('Connecting to Slack RTM API....')
		success, resp = self.api_call('rtm.start')
		if success:
			self._ws_url = resp['url']
			ws = websocket.WebSocketApp(self._ws_url,
						on_message = self._on_message,
						on_error = self._on_error,
						on_close = self._on_close)
			self._ws = WSocket(ws, self._connected)
			self._ws.start()
			_log.debug('Connected to Slack RTM API')
			return True
		_log.error('Failed to connect to Slack RTM API')
		return False

	def _on_message(self, ws, message):
		parsed = json.loads(message)
		if not parsed['type'] in config.slack.ignore:
			self._output.put(parsed)

	def _on_close(self, ws):
		self._ws.join()
		if self._connected.is_set():
			_log.error('websocket closed unexpectedly, reconnecting...')
			self.rtm_connect()
		else:
			_log.debug('websocket closed expectedly')
			

	def _on_error(self, ws, error):
		_log.error('websocket error: %s'%error)

	def rtm_read(self, block = True, timeout = 5):
		try:
			return self._output.get(block = block, timeout=timeout)
		except Empty:
			return None

	@property
	def rtm_connected(self):
		return self._connected.is_set()

	def rtm_close(self):
		self._connected.clear()
		self._ws.close()

	def as_user(self, token):
		return SlackClient(token)