import chat

def broadcastMessageAdded(message):
	try:
		chat.schema.OnMessageAdded.broadcast(
        # Subscription group to notify clients in.
		    group="ON_MESSAGE_ADDED",
		    # Dict delivered to the `publish` method.
		    payload={'message' : message},
		)
	except:
		pass