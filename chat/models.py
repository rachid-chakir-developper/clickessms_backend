from django.db import models

# Create your models here.
class Conversation(models.Model):
	name = models.TextField(default='', null=True)
	creator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class ParticipantConversation(models.Model):
	conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, related_name='participants', null=True)
	user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='participantconversation', null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)

# Create your models here.
class Message(models.Model):
	text = models.TextField(null=True)
	conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, related_name='messages', null=True)
	sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
	is_read = models.BooleanField(default=False, null=True)
	is_seen = models.BooleanField(default=False, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, null=True)
	
	class Meta:
		ordering = ['-created_at']