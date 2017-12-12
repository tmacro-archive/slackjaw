def duplicate_reaction(event, user):
	return user.react(event['item']['channel'], event['item']['ts'], event['reaction'])
