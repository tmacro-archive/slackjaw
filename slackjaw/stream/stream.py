from ..util.config import config
from ..util.log import getLogger

_log = getLogger('slack_reader')

				

class Stream:
	def __init__(self, slack, *args):
		self._slack = slack
		self._filters = args
		self._log = _log.getChild('stream')

	def register(self, fltr):
		self._log.debug('registering filter: %s'%filter)
		self._filters.append(fltr)
	
	def _match(self, event):
		topics = [fltr.topic for fltr in self._filters if fltr(event)]
		return list(set(topics))

	def __call__(self):
		for event in self._slack.events:
			topics = self._match(event)
			if topics:
				yield event, topics

# r = Reader(config.crypto.slack)
# r.start()

# cmd_filter = RegexFilter(text = '^![a-z]+', id = 'CMD_FILTER', topic = 'cmd', user = True)
# ch_filter = ChannelFilter(type = 'message', id = "CH_FILTER", topic = "ch_", user = True)
# msg_filter = Filter(type = 'message', id = 'MSG_FILTER', topic = 'msg', user = True)
# at_filter = AtFilter(text = '^<@(?P<user>\w+)>', id = 'AT_FILTER', topic = 'cmd', user = True, bot = r._id)

# s = Stream(cmd_filter, ch_filter, msg_filter, at_filter)
# p = Publisher('tcp://*:4930')
# p.open()
# for event, topics in s(r.events):
# 	if topics:
# 		p.publish('firehose', event)
# 	for topic in topics:
# 		p.publish(topic, event)