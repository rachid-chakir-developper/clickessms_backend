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
			title = "Demande d'ntervention mise à jour."
			message = "Votre demande intervention a été mise à jour."
		if action == 'TO_DO':
			notification_type = "TASK_TO_DO"
			title = "Nouvelle intervention assignée."
			message = "Vous avez une nouvelle intervention assignée."
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
			title = "Votre intervention assignée."
			message = "Vous avez une nouvelle intervention assignée."
		elif task.status == 'IN_PROGRESS':
			notification_type = "TASK_IN_PROGRESS"
			title = "Intervention commencée."
			message = "Une intervention vient d'être commencée."
		elif task.status == 'COMPLETED':
			notification_type = "TASK_COMPLETED"
			title = "Intervention finie."
			message = "Une intervention vient d'être finie."
		else:
			return 0
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

def notify_expense(sender, recipient, expense, action=None):
	"""
	Fonction pour notifier les utilisateurs des actions ou mises à jour relatives à une dépense.
	
	:param sender: L'utilisateur qui envoie la notification
	:param recipient: L'utilisateur qui reçoit la notification
	:param expense: L'instance de la dépense concernée
	:param action: L'action effectuée (par exemple, "CREATED" ou "UPDATED")
	"""
	if sender == recipient:
		return 0  # Pas de notification si l'expéditeur et le destinataire sont les mêmes

	if action:
		notification_type = "EXPENSE_ADDED"
		title = "Nouvelle demande de dépense ajoutée."
		message = f"Une nouvelle demande de dépense a été soumise."

		if action == 'UPDATED':
			notification_type = "EXPENSE_UPDATED"
			title = "Demande de dépense mise à jour."
			message = f"Votre demande de dépense a été mise à jour."
	else:
		if expense.status == 'PENDING':
			notification_type = "EXPENSE_PENDING"
			title = "Demande de dépense en attente d'approbation."
			message = f"Votre demande de dépense est en attente d'approbation."
		elif expense.status == 'APPROVED':
			notification_type = "EXPENSE_APPROVED"
			title = "Demande de dépense approuvée."
			message = f"Votre demande de dépense a été approuvée."
		elif expense.status == 'REJECTED':
			notification_type = "EXPENSE_REJECTED"
			title = "Demande de dépense rejetée."
			message = f"Votre demande de dépense a été rejetée."
		elif expense.status == 'PAID':
			notification_type = "EXPENSE_PAID"
			title = "Dépense payée."
			message = f"La dépense a été marquée comme payée."
		elif expense.status == 'UNPAID':
			notification_type = "EXPENSE_UNPAID"
			title = "Dépense non payée."
			message = f"La dépense est marquée comme non payée."
		else:
			return 0  # Aucune notification si le statut est inconnu ou non pertinent

	# Construire les données de notification
	notification_data = {
		"sender": sender,
		"recipient": recipient,
		"notification_type": notification_type,
		"title": title,
		"message": message,
		"expense": expense,
	}

	# Appeler la fonction de notification
	notify(notification_data)

def notify_expense_report(sender, recipient, expense_report, action=None):
    """
    Fonction pour notifier les utilisateurs des actions ou mises à jour relatives à une dépense.
    
    :param sender: L'utilisateur qui envoie la notification
    :param recipient: L'utilisateur qui reçoit la notification
    :param expense_report: L'instance de la dépense concernée
    :param action: L'action effectuée (par exemple, "CREATED" ou "UPDATED")
    """
    if sender == recipient:
        return 0  # Pas de notification si l'expéditeur et le destinataire sont les mêmes

    if action:
        notification_type = "EXPENSE_REPORT_ADDED"
        title = "Nouvelle note de frais créée"
        message = f"Une nouvelle note de frais a été créée et soumise pour approbation."

        if action == 'UPDATED':
            notification_type = "EXPENSE_REPORT_UPDATED"
            title = "Note de frais mise à jour"
            message = f"Votre note de frais a été mise à jour avec succès."
    else:
        if expense_report.status == 'PENDING':
            notification_type = "EXPENSE_REPORT_PENDING"
            title = "Note de frais en attente"
            message = f"Votre note de frais est en attente d'approbation par le responsable."
        elif expense_report.status == 'APPROVED':
            notification_type = "EXPENSE_REPORT_APPROVED"
            title = "Note de frais approuvée"
            message = f"Votre note de frais a été approuvée. Vous recevrez un remboursement sous peu."
        elif expense_report.status == 'REJECTED':
            notification_type = "EXPENSE_REPORT_REJECTED"
            title = "Note de frais rejetée"
            message = f"Votre note de frais a été rejetée. Veuillez vérifier et soumettre une nouvelle version."
        elif expense_report.status == 'REIMBURSED':
            notification_type = "EXPENSE_REPORT_REIMBURSED"
            title = "Note de frais remboursée"
            message = f"Votre note de frais a été remboursée. Vérifiez votre compte pour confirmation."
        else:
            return 0  # Aucune notification si le statut est inconnu ou non pertinent

    # Construire les données de notification
    notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "expense_report": expense_report,
    }

    # Appeler la fonction de notification
    notify(notification_data)

def notify_beneficiary_admission(sender, recipient, beneficiary_admission, action=None):
    """
    Notifie les utilisateurs des actions ou mises à jour relatives à une demande d'admission.

    :param sender: L'utilisateur envoyant la notification
    :param recipient: L'utilisateur recevant la notification
    :param beneficiary_admission: L'instance de BeneficiaryAdmission concernée
    :param action: L'action effectuée (par exemple, "CREATED" ou "UPDATED")
    """
    if sender == recipient:
        return 0  # Pas de notification si l'expéditeur et le destinataire sont les mêmes

    if action:
        notification_type = "BENEFICIARY_ADMISSION_ADDED"
        title = "Nouvelle demande d'admission créée"
        message = "Une nouvelle demande d'admission a été créée et soumise pour examen."

        if action == "UPDATED":
            notification_type = "BENEFICIARY_ADMISSION_UPDATED"
            title = "Demande d'admission mise à jour"
            message = "La demande d'admission a été mise à jour avec succès."
    else:
        if beneficiary_admission.status == "NEW":
            notification_type = "BENEFICIARY_ADMISSION_NEW"
            title = "Nouvelle demande d'admission"
            message = "Une nouvelle demande d'admission a été soumise pour examen."
        elif beneficiary_admission.status == "PENDING":
            notification_type = "BENEFICIARY_ADMISSION_PENDING"
            title = "Demande d'admission en attente"
            message = "La demande d'admission est en attente d'évaluation."
        elif beneficiary_admission.status == "APPROVED":
            notification_type = "BENEFICIARY_ADMISSION_APPROVED"
            title = "Demande d'admission approuvée"
            message = "La demande d'admission a été approuvée. L'admission est prévue comme indiqué."
        elif beneficiary_admission.status == "REJECTED":
            notification_type = "BENEFICIARY_ADMISSION_REJECTED"
            title = "Demande d'admission rejetée"
            message = "La demande d'admission a été rejetée. Veuillez consulter les commentaires et soumettre une nouvelle demande si nécessaire."
        elif beneficiary_admission.status == "CANCELED":
            notification_type = "BENEFICIARY_ADMISSION_CANCELED"
            title = "Demande d'admission annulée"
            message = "La demande d'admission a été annulée par le demandeur ou l'administrateur."
        else:
            return 0  # Aucune notification si le statut est inconnu ou non pertinent

    # Construire les données de notification
    notification_data = {
        "sender": sender,
        "recipient": recipient,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "beneficiary_admission": beneficiary_admission,
    }

    # Appeler la fonction de notification
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
