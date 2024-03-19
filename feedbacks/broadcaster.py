import feedbacks

def broadcastCommentAdded(comment):
	try:
		feedbacks.schema.OnCommentAdded.broadcast(
        # Subscription group to notify clients in.
		    group="ON_COMMENT_ADDED",
		    # Dict delivered to the `publish` method.
		    payload={'comment' : comment},
		)
	except:
		pass

def broadcastCommentDeleted(comment):
	try:
		feedbacks.schema.OnCommentDeleted.broadcast(
        # Subscription group to notify clients in.
		    group="ON_COMMENT_DELETED",
		    # Dict delivered to the `publish` method.
		    payload={'comment' : comment},
		)
	except:
		pass