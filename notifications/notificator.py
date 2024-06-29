from django.conf import settings
import threading
import requests
import json

from django.db.models import Q

from notifications.models import Notification, MessageNotification
from accounts.models import Device
import notifications

def notify(notification_data):
	notification = Notification.objects.create(**notification_data)
	try:
		notifications.schema.OnNotificationAdded.broadcast(
        # Subscription group to notify clients in.
		    group="ON_NOTIF_ADDED",
		    # Dict delivered to the `publish` method.
		    payload=notification,
		)
		push_notification(notification_data)
	except Exception as e:
		pass

def broadcastNotificationsSeen(not_seen_count=0):
	try:
		notifications.schema.OnNotificationsSeen.broadcast(
        # Subscription group to notify clients in.
		    group="ON_NOTIFS_SEEN",
		    # Dict delivered to the `publish` method.
		    payload={'not_seen_count' : not_seen_count},
		)
	except:
		pass
def broadcastMessageNotificationAdded(message_notification):
    try:
        message_notifications.schema.OnMessageNotificationAdded.broadcast(
        # Subscription group to notify clients in.
            group="ON_MSG_NOTIF_ADDED",
            # Dict delivered to the `publish` method.
            payload=message_notification,
        )
    except Exception as e:
        pass

def broadcastMessageNotificationsSeen(not_seen_count=0):
    try:
        message_notifications.schema.OnMessageNotificationsSeen.broadcast(
        # Subscription group to notify clients in.
            group="ON_MSG_NOTIFS_SEEN",
            # Dict delivered to the `publish` method.
            payload={'not_seen_count' : not_seen_count},
        )
    except:
        pass

def push_notification(notification=None, device_tokens=[]):
	try:
		if device_tokens and len(device_tokens) > 0:
			# print(f'device_tokensdevice_tokensdevice_tokens= {device_tokens}')
			url = "https://fcm.googleapis.com/fcm/send"
			headers = {
				"Content-Type": "application/json",
				"Authorization": f"key={settings.FCM_KEY}",
			}
			data = {
	        	"registration_ids": device_tokens,
	        	"notification": {
		            'title': notification['title'],
		            'body': notification['message'],
		        },
	    	}
			response = requests.post(url, data=json.dumps(data), headers=headers)
			# print(f"response.json() => {response.json()}")
	except Exception as e:
		print(f'Exception push_notification {e}')


def push_notification_to_employees(notification=None, employees=[]):
	def start_sending_push_notification():
		try:
			device_tokens = Device.objects.filter(user__employee__in=employees, is_user_online_here=True).values_list('token', flat=True)
			push_notification(notification=notification, device_tokens=list(device_tokens))
		except Exception as e:
			print(f'Exception start_sending_push_notification {e}')

	try:
		thread = threading.Thread(target=start_sending_push_notification, daemon=True, name='push_notification_task')
		thread.start()
	except Exception as e:
		pass

def push_notification_chat_participants(message):
	# try:
	# 	device_tokens = Device.objects.filter(
	# 		~Q(user_id=message.sender.id),
	# 		user__participantconversation__conversation_id=message.conversation.id,
	# 		is_user_online_here=True
	# 	).values_list('token', flat=True)
	# 	print(f'device_tokens {list(device_tokens)}')
	# except Exception as e:
	# 	print(f'Exception device_tokens {e}')
	def start_sending_push_notification():
		try:
			notification = {
                "title": f"{message.sender.first_name} {message.sender.last_name}",
                "message": f"{message.text}"
            }
			device_tokens = Device.objects.filter(
				~Q(user_id=message.sender.id),
				user__participantconversation__conversation_id=message.conversation.id,
				is_user_online_here=True
			).values_list('token', flat=True)
			push_notification(notification=notification, device_tokens=list(device_tokens))
		except Exception as e:
			print(f'Exception start_sending_push_notification {e}')

	try:
		thread = threading.Thread(target=start_sending_push_notification, daemon=True, name='push_notification_chat')
		thread.start()
	except Exception as e:
		pass
