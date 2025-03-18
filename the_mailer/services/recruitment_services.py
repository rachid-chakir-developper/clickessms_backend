from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_interview_invitation(meeting):
    """Envoie un email d'invitation à un entretien pour un candidat."""

    # Vérification si la réunion est bien un entretien candidat
    if meeting.meeting_mode != "CANDIDATE_INTERVIEW" or not meeting.job_candidate:
        return False  # Ne pas envoyer si ce n'est pas un entretien candidat

    candidat = meeting.job_candidate

    if not candidat.email:
        return False  # Pas d'email, pas d'envoi

    subject = "Invitation à un entretien"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [candidat.email]

    # Charger le template HTML
    html_content = render_to_string("recruitment/interview_invitation.html", {
        "first_name": candidat.first_name,  # Prénom du candidat
        "interview_date": meeting.starting_date_time.date(),
        "interview_time": meeting.starting_date_time.time(),
        "interview_location": meeting.video_call_link or "Lieu précisé ultérieurement"
    })

    # Création de l'email
    email = EmailMultiAlternatives(subject, "Votre client email ne supporte pas les emails HTML.", from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Envoi de l'email
    email.send()
    return True  # Email envoyé avec succès


def send_job_candidate_information_sheet_email(candidate_sheet):
    """Envoie un email au candidat pour remplir sa fiche de renseignement."""

    if not candidate_sheet.access_token:
        candidate_sheet.generate_access_token()

    access_link = candidate_sheet.get_access_link()
    expiration_date = candidate_sheet.token_expiration.strftime('%d/%m/%Y')

    if not candidate_sheet.email:
        return False

    subject = "Complétez votre fiche de renseignement"
    from_email = settings.DEFAULT_FROM_EMAIL
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

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    email.send()
    return True  # Email envoyé avec succès


def send_application_interest_email(job_candidate_application):
    """Envoie un email au candidat pour lui notifier que son profil nous intéresse."""
    
    # Vérification que le candidat a bien un email
    if not job_candidate_application.email:
        return False  # Pas d'email, pas d'envoi

    subject = "Votre candidature nous intéresse"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [job_candidate_application.email]

    # Charger le template HTML
    html_content = render_to_string("recruitment/application_interest.html", {
        "first_name": job_candidate_application.first_name
    })

    # Création de l'email
    email = EmailMultiAlternatives(subject, "Votre client email ne supporte pas les emails HTML.", from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Envoi de l'email
    email.send()
    return True  # Email envoyé avec succès

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_application_rejection_email(job_candidate_application):
    """Envoie un email au candidat pour l'informer que sa candidature a été refusée."""

    if not job_candidate_application.email:
        return False  # Pas d'email, pas d'envoi

    subject = "Statut de votre candidature"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [job_candidate_application.email]

    html_content = render_to_string("recruitment/application_rejected.html", {
        "first_name": job_candidate_application.first_name,
        "job_title": job_candidate_application.job_title
    })

    email = EmailMultiAlternatives(subject, "Votre client email ne supporte pas les emails HTML.", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    return True  # Email envoyé avec succès


def send_application_acceptance_email(job_candidate_application):
    """Envoie un email au candidat pour l'informer que sa candidature a été acceptée."""

    if not job_candidate_application.email:
        return False  # Pas d'email, pas d'envoi

    subject = "Votre candidature a été acceptée"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [job_candidate_application.email]

    html_content = render_to_string("recruitment/application_accepted.html", {
        "first_name": job_candidate_application.first_name,
        "job_title": job_candidate_application.job_title,
    })

    email = EmailMultiAlternatives(subject, "Votre client email ne supporte pas les emails HTML.", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    return True  # Email envoyé avec succès



