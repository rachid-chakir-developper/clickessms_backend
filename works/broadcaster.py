import works

def broadcastTicketAdded(ticket):
	try:
		works.schema.OnTicketAdded.broadcast(
        # Subscription group to notify clients in.
		    group="ON_TICKET_ADDED",
		    # Dict delivered to the `publish` method.
		    payload=ticket,
		)
	except:
		pass

def broadcastTicketUpdated(ticket):
	try:
		works.schema.OnTicketUpdated.broadcast(
        # Subscription group to notify clients in.
		    group="ON_TICKET_UPDATED",
		    # Dict delivered to the `publish` method.
		    payload=ticket,
		)
	except:
		pass

def broadcastTicketDeleted(ticket):
	try:
		works.schema.OnTicketDeleted.broadcast(
        # Subscription group to notify clients in.
		    group="ON_TICKET_DELETED",
		    # Dict delivered to the `publish` method.
		    payload=ticket,
		)
	except:
		pass