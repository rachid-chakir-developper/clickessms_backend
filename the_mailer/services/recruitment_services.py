from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from the_mailer.services.mail_services import send_this_email

def send_interview_invitation(meeting):
    """Envoie un email d'invitation à un entretien pour un candidat."""

    try:
        # Vérification si la réunion est bien un entretien candidat
        if meeting.meeting_mode != "CANDIDATE_INTERVIEW" or not meeting.job_candidate:
            return False  # Ne pas envoyer si ce n'est pas un entretien candidat

        candidat = meeting.job_candidate

        if not candidat.email:
            return False  # Pas d'email, pas d'envoi

        subject = "Invitation à un entretien"
        to_email = [candidat.email]

        # Charger le template HTML
        html_content = render_to_string("recruitment/interview_invitation.html", {
            "first_name": candidat.first_name,  # Prénom du candidat
            "interview_date": meeting.starting_date_time.date(),
            "interview_time": meeting.starting_date_time.time(),
            "interview_location": meeting.video_call_link or "Lieu précisé ultérieurement"
        })

        return send_this_email(subject=subject, html_content=html_content, to_email=to_email)  # Email envoyé 
    except Exception as e:
        return False



def send_job_candidate_information_sheet_email(candidate_sheet):
    """Envoie un email au candidat pour remplir sa fiche de renseignement."""

    try:
        if not candidate_sheet.access_token:
            candidate_sheet.generate_access_token()

        access_link = candidate_sheet.get_access_link()
        expiration_date = candidate_sheet.token_expiration.strftime('%d/%m/%Y')

        if not candidate_sheet.email:
            return False

        subject = "Complétez votre fiche de renseignement"
        to_email = [candidate_sheet.email]

        html_content = render_to_string("recruitment/job_candidate_information_sheet_invitation.html", {
            "first_name": candidate_sheet.first_name,
            "access_link": access_link,
            "expiration_date": expiration_date,
        })

        text_content = f"""
        Bonjour {candidate_sheet.first_name},

        Vous avez été invité à remplir votre fiche de renseignement pour le processus de recrutement.

        Cliquez sur le lien suivant pour accéder à votre fiche :
        {access_link}

        Ce lien est valable jusqu'au {expiration_date}.

        Cordialement,
        L'équipe RH
        """
        return send_this_email(subject=subject, html_content=html_content, to_email=to_email)

    except Exception as e:
        return False



def send_application_interest_email(job_candidate_application):
    """Envoie un email au candidat pour lui notifier que son profil nous intéresse."""
    
    try:
        # Vérification que le candidat a bien un email
        if not job_candidate_application.email:
            return False  # Pas d'email, pas d'envoi

        subject = "Votre candidature nous intéresse"
        to_email = [job_candidate_application.email]

        # Charger le template HTML
        html_content = render_to_string("recruitment/application_interest.html", {
            "first_name": job_candidate_application.first_name
        })


        return send_this_email(subject=subject, html_content=html_content, to_email=to_email)  # Email envoyé
    except Exception as e:
        return False



def send_application_rejection_email(job_candidate_application):
    """Envoie un email au candidat pour l'informer que sa candidature a été refusée."""

    try:
        if not job_candidate_application.email:
            return False  # Pas d'email, pas d'envoi

        subject = "Statut de votre candidature"
        to_email = [job_candidate_application.email]

        html_content = render_to_string("recruitment/application_rejected.html", {
            "first_name": job_candidate_application.first_name,
            "job_title": job_candidate_application.job_title
        })


        return send_this_email(subject=subject, html_content=html_content, to_email=to_email)  # Email envoyé
    except Exception as e:
        return False



def send_application_acceptance_email(job_candidate_application,):
    
    """Envoie un email au candidat pour l'informer que sa candidature a été acceptée."""
    try:
        if not job_candidate_application.email:
            return False  # Pas d'email, pas d'envoi

        subject = "Votre candidature a été acceptée"
        to_email = [job_candidate_application.email]

        html_content = render_to_string("recruitment/application_accepted.html", {
            "first_name": job_candidate_application.first_name,
            "job_title": job_candidate_application.job_title,
        })


        return send_this_email(subject=subject, html_content=html_content, to_email=to_email)  # Email envoyé
    except Exception as e:
        return False

def get_default_sent_email(job_candidate_application):
    """Retourne les informations de l'email à envoyer selon le statut de la candidature."""
    try:
        if job_candidate_application.status == "REJECTED":
            subject = "Statut de votre candidature"
            body = render_to_string("recruitment/application_rejected.html", {
                "first_name": job_candidate_application.first_name,
                "job_title": job_candidate_application.job_title
            })

        elif job_candidate_application.status == "INTERESTED":
            subject = "Votre candidature nous intéresse"
            body = render_to_string("recruitment/application_interest.html", {
                "first_name": job_candidate_application.first_name,
            })

        elif job_candidate_application.status == "ACCEPTED":
            job_position = job_candidate_application.job_position
            job_candidate = job_candidate_application.job_candidate
            job_candidate_information_sheet = job_candidate.job_candidate_information_sheets.filter(job_position=job_position).order_by('-created_at').first()
            job_candidate_information_sheet.generate_access_token()
            access_link = job_candidate_information_sheet.get_access_link()
            expiration_date = job_candidate_information_sheet.token_expiration.strftime('%d/%m/%Y') if job_candidate_information_sheet.token_expiration else ''
            subject = "Votre candidature a été acceptée / Complétez votre fiche de renseignement"
            body = render_to_string("recruitment/application_accepted.html", {
                "first_name": job_candidate_information_sheet.first_name,
                "job_title": job_candidate_information_sheet.job_position.title,
                "access_link": access_link,
                "expiration_date": expiration_date,
            })

        elif job_candidate_application.status == "INTERVIEW":
            job_position = job_candidate_application.job_position
            job_candidate = job_candidate_application.job_candidate
            meeting = job_candidate.job_candidate_meetings.filter(job_position=job_position).order_by('-created_at').first()
            candidat = meeting.job_candidate
            subject = "Invitation à un entretien"
            body = render_to_string("recruitment/interview_invitation.html", {
                "first_name": candidat.first_name,  # Prénom du candidat
                "interview_date": meeting.starting_date_time.date(),
                "interview_time": meeting.starting_date_time.time(),
                "interview_location": meeting.video_call_link or "Lieu précisé ultérieurement"
            })

        else:
            return "", "", ""  # Pas d'email par défaut si la candidature est en attente

        return job_candidate_application.email, subject, body
    except Exception as e:
        raise e



