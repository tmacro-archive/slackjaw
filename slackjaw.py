from slackjaw.stream import Reader, Filter, Stream
from slackjaw.util.config import config
from slackjaw.react import duplicate_reaction, join_room, leave_room
from slackjaw.slack import SlackClient
from slackjaw.slack import SlackUser

r = Reader(config.crypto.slack)
r.start()

bots = [SlackUser(token) for token in config.crypto.bots]
user = SlackUser(config.crypto.slack)

# msg_filter = Filter(type = 'message', id = 'MSG_FILTER', topic = 'msg', user = True)
emoji_filter = Filter(type = 'reaction_added', id = 'EMOJI_FILTER', topic = 'reaction', user = user.id)

s = Stream(r, emoji_filter)


for event, topics in s():
	if topics:
		if 'reaction' in topics:
			channel = event['item']['channel']
			for bot in bots:
				print('-'*50)
				if not bot.join(channel):
					if not user.invite(channel, bot.id):
						continue
				duplicate_reaction(event, bot)
				bot.leave(channel)
				print('-'*50)
