from slackjaw.stream import Reader, Filter, Stream
from slackjaw.util.config import config
from slackjaw.react import duplicate_reaction, join_room, leave_room
from slackjaw.slack import SlackClient

r = Reader(config.crypto.slack)
r.start()

msg_filter = Filter(type = 'message', id = 'MSG_FILTER', topic = 'msg', user = True)
emoji_filter = Filter(type = 'reaction_added', id = 'EMOJI_FILTER', topic = 'reaction', user = True)
s = Stream(r, msg_filter, emoji_filter)

bots = []
for token in config.crypto.bots:
    success, resp = SlackClient(token).as_user(token).api_call('auth.test')
    print(resp)
    if not success:
        raise Exception('Invalid slack credentials')
    bots.append((resp['user_id'], token))

for event, topics in s():
    if topics:
        if 'reaction' in topics:
            channel = event['item']['channel']
            for bot, token in bots:
                join_room(channel, bot, token)
                duplicate_reaction(event, token)
                leave_room(channel, token)
