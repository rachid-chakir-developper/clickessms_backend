import os.path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

from django.conf import settings

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_google_calendar_service():
    try:
        key_file_path = settings.BASE_DIR / 'feedbacks/djangocalendar-412715-276727682242.json'
        # Créez un objet credentials à partir du fichier de clé privée
        credentials = service_account.Credentials.from_service_account_file(
            key_file_path,
            scopes=SCOPES,
        )

        # Créez un service Google Calendar
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print('Erreur lors de create_google_calendar_service:', e)

def create_calendar_event_task(task):
    service = create_google_calendar_service()

    # Créez un événement à partir des détails de la tâche
    event = {
        'summary': task.name,
        'location': task.address,
        'description': task.description,
        'start': {
            'dateTime': task.starting_date_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': task.ending_date_time.isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': 'rachid@clikea.fr'},
            # {'email': 'participant2@example.com'},
            # Ajoutez d'autres participants si nécessaire
        ],
        'visibility': 'public',
        'sendUpdates': 'all',
    }

    # Ajoutez l'événement au calendrier Google
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Événement ajouté: %s' % (event.get('htmlLink')))
        return event
    except Exception as e:
        print('Erreur lors de l\'ajout de l\'événement:', e)
        return None

def update_calendar_event_task(task):
    service = create_google_calendar_service()

    # ID de l'événement à mettre à jour (assurez-vous que task.google_calendar_event_id est correct)
    event_id = task.google_calendar_event_id

    # Créez un événement à partir des détails mis à jour de la tâche
    updated_event = {
        'summary': task.name,
        'location': task.address,
        'description': task.description,
        'start': {
            'dateTime': task.starting_date_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': task.ending_date_time.isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': 'rasheed.shakeer@gmail.com'},
            # {'email': 'participant2_updated@example.com'},
            # Ajoutez d'autres participants mis à jour si nécessaire
        ],
        'visibility': 'public',
        'sendUpdates': 'all',
    }

    try:
        if event_id and event_id is not None:
            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=updated_event).execute()
            print('Événement mis à jour: %s' % (updated_event.get('htmlLink')))
            return updated_event
        else:
            create_calendar_event_task(task=task)
    except Exception as e:
        print('Erreur lors de la mise à jour de l\'événement:', e)
        return None

def delete_calendar_event_task(task):
    service = create_google_calendar_service()

    # ID de l'événement à supprimer (assurez-vous que task.google_calendar_event_id est correct)
    event_id = task.google_calendar_event_id

    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f'Événement supprimé: {event_id}')
    except Exception as e:
        print('Erreur lors de la suppression de l\'événement:', e)
