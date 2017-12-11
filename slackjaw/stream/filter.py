import re
from ..util.log import getLogger

_log = getLogger('stream.filter')

class Filter(object):
	params = ['type', 'user', 'channel', 'text']
	def __init__(self, **kwargs):
		self._filter = {}
		self._id = kwargs.pop('id') if 'id' in kwargs else 'Filter'
		self._topic = kwargs.pop('topic') if 'topic' in kwargs else 'firehose'
		self._log = _log.getChild(self._id)
		for param in Filter.params:
			 v = kwargs.get(param)
			 if v:
			 	self._filter[param] = v

	@property
	def topic(self):
		return self._topic

	def _check(self, k, v, msg):
		print('Checking %s, %s %s'%(k, v, msg))
		if isinstance(v, bool):
			return k in msg.keys()
		if v in msg.get(k, ''):
			return True
		return False

	def __call__(self, msg):
		passed = True
		for k, v in self._filter.items():
			if not self._check(k,v,msg):
				passed = False
				break
		return passed

class RegexFilter(Filter):
	def __init__(self, **kwargs):
		Filter.__init__(self, **kwargs)
		compiled = dict()
		for k,v in self._filter.items():
			if isinstance(v, str):
				compiled[k] = re.compile(v)
		self._filter.update(compiled)

	def _check(self, k, v, msg):
		if isinstance(v, bool):
			return k in msg.keys()
		if re.match(v, msg.get(k, '')) is None:
			return False
		return True

class ChannelFilter(Filter):
	@property
	def topic(self):
		return self._topic + self._lastCh

	def _check(self,k,v, msg):
		if 'channel' in msg:
			self._lastCh = msg.get('channel')
		return super(ChannelFilter, self)._check(k,v,msg)

class AtFilter(RegexFilter):
	def __init__(self, bot = None, **kwargs):
		super(AtFilter, self).__init__(**kwargs)
		self._bot = bot
	def _check(self, k, v, msg):
		if isinstance(v, bool):
			return k in msg.keys()
		match = re.match(v, msg.get(k, ''))
		if match and match.group('user') == self._bot:
			return True
		return False

class TrueFilter(Filter):
	def _check(self, k, v, msg):
		return True