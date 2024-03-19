import accounts

def broadcastUserUpdated(user):
	try:
		accounts.schema.OnUserUpdated.broadcast(
        # Subscription group to notify clients in.
		    group="ON_USER_UPDATED",
		    # Dict delivered to the `publish` method.
		    payload=user,
		)
	except:
		pass


def broadcastUserCurrentLocalisationAsked(is_asked=False):
	try:
		accounts.schema.OnUserCurrentLocalisationAsked.broadcast(
        # Subscription group to notify clients in.
		    group="ON_USER_LOCALISATION_ASKED",
		    # Dict delivered to the `publish` method.
		    payload={'is_asked' : is_asked},
		)
	except:
		pass