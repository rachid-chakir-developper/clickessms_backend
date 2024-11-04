import qualities

def broadcastUndesirableEventAdded(undesirable_event):
	try:
		qualities.schema.OnUndesirableEventAdded.broadcast(
        # Subscription group to notify clients in.
		    group="ON_EI_ADDED",
		    # Dict delivered to the `publish` method.
		    payload=undesirable_event,
		)
	except:
		pass

def broadcastUndesirableEventUpdated(undesirable_event):
	try:
		qualities.schema.OnUndesirableEventUpdated.broadcast(
        # Subscription group to notify clients in.
		    group="ON_EI_UPDATED",
		    # Dict delivered to the `publish` method.
		    payload=undesirable_event,
		)
	except:
		pass

def broadcastUndesirableEventDeleted(undesirable_event):
	try:
		qualities.schema.OnUndesirableEventDeleted.broadcast(
        # Subscription group to notify clients in.
		    group="ON_EI_DELETED",
		    # Dict delivered to the `publish` method.
		    payload=undesirable_event,
		)
	except:
		pass