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

def notify_undesirable_event(sender, recipient, undesirable_event, action=None):
	if sender==recipient:
		return 0
	if action:
		notification_type = "EI_ADDED"
		title = "Événement indésirable déclaré"
		message = "Un événement indésirable a été déclaré."
		if action == 'UPDATED':
			notification_type = "EI_UPDATED"
			title = "Événement indésirable mise à jour."
			message = "Votre événement indésirable a été mise à jour."
	else:
		if undesirable_event.status == 'NEW':
			notification_type = "EI_NEW"
			title = "Événement indésirable remis comme déclaré."
			message = "Votre événement indésirable est remis comme déclaré."
		if undesirable_event.status == 'IN_PROGRESS':
			notification_type = "EI_IN_PROGRESS"
			title = "Événement indésirable en cours de traitement."
			message = "Votre événement indésirable est en cours de traitement."
		if undesirable_event.status == 'DONE':
			notification_type = "EI_DONE"
			title = "Événement indésirable traité."
			message = "Votre événement indésirable a été traité."
	notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "undesirable_event": undesirable_event,
    }
	notify(notification_data)

def notify_employee_task_action(sender, recipient, task_action):
	if sender==recipient:
		return 0
	notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": "TASK_ACTION_ADDED",
        "title": "Nouvelle action assignée",
        "message": "Vous avez une nouvelle action assignée.",
        "task_action": task_action,
    }
	notify(notification_data)

def notify_employee_absence(sender, recipient, employee_absence, action=None):
	if sender==recipient:
		return 0
	if action:
		notification_type = "EMPLOYEE_ABSENCE_ADDED"
		title = "Nouvelle demande de congé ajoutée."
		message = "Une nouvelle demande de congé a été soumise."
		if action == 'UPDATED':
			notification_type = "EMPLOYEE_ABSENCE_UPDATED"
			title = "Demande de congé mise à jour."
			message = "Votre demande de congé a été mise à jour."
	else:
		if employee_absence.status == 'PENDING':
			notification_type = "EMPLOYEE_ABSENCE_PENDING"
			title = "Demande de congé en attente de décision."
			message = "Votre demande de congé est en attente de décision."
		if employee_absence.status == 'APPROVED':
			notification_type = "EMPLOYEE_ABSENCE_APPROVED"
			title = "Demande de congé approuvée."
			message = "Votre demande de congé a été approuvée."
		elif employee_absence.status == 'REJECTED':
			notification_type = "EMPLOYEE_ABSENCE_REJECTED"
			title = "Demande de congé rejetée."
			message = "Votre demande de congé a été rejetée."
	notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "employee_absence": employee_absence,
    }
	notify(notification_data)

def notify_task(sender, recipient, task, action=None):
	if sender == recipient:
		return 0
	if action:
		notification_type = "TASK_ADDED"
		title = "Nouvelle demande d'intervention ajoutée."
		message = "Une nouvelle demande d'intervention a été soumise."
		if action == 'UPDATED':
			notification_type = "TASK_UPDATED"
			title = "Intervention mise à jour."
			message = "Votre intervention a été mise à jour."
	else:
		if task.status == 'PENDING':
			notification_type = "TASK_PENDING"
			title = "Demande d'intervention en attente de décision."
			message = "Votre demande d'intervention est en attente de décision."
		elif task.status == 'APPROVED':
			notification_type = "TASK_APPROVED"
			title = "Demande d'intervention approuvée."
			message = "Votre demande d'intervention a été approuvée."
		elif task.status == 'REJECTED':
			notification_type = "TASK_REJECTED"
			title = "Demande d'intervention rejetée."
			message = "Votre demande d'intervention a été rejetée."
		elif task.status == 'TO_DO':
			notification_type = "TASK_TO_DO"
			title = "Nouvelle tâche assignée."
			message = "Vous avez une nouvelle tâche assignée."
		elif task.status == 'IN_PROGRESS':
			notification_type = "TASK_IN_PROGRESS"
			title = "Intervention commencée."
			message = "Une intervention vient d'être commencée."
		elif task.status == 'COMPLETED':
			notification_type = "TASK_COMPLETED"
			title = "Intervention finie."
			message = "Une intervention vient d'être finie."
	notification_data = {
		"sender": sender,
		"recipient": recipient,
		"notification_type": notification_type,
		"title": title,
		"message": message,
		"task": task
	}
	notify(notification_data)

def notify_employee_meeting_decision(sender, recipient, meeting_decision):
	if sender==recipient:
		return 0
	notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": "MEETING_DECISION_ADDED",
        "title": "Nouvelle décision assignée",
        "message": "Vous avez une nouvelle décision assignée.",
        "meeting_decision": meeting_decision,
    }
	notify(notification_data)

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

def broadcastMessageNotificationsRead(not_read_count=0):
    try:
        message_notifications.schema.OnMessageNotificationsRead.broadcast(
        # Subscription group to notify clients in.
            group="ON_MSG_NOTIFS_READ",
            # Dict delivered to the `publish` method.
            payload={'not_read_count' : not_read_count},
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
