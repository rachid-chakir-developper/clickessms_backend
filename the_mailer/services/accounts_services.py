from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def get_default_sent_email(user, default_password):
    """Retourne les informations de l'email à envoyer selon le statut de la candidature."""
    try:
        if user.is_must_change_password:
            subject = "Bienvenue sur ROBERP"
            body = render_to_string("accounts/first_connexion_infos.html", {
                "user": user,
                "default_password": default_password
            })

        elif not user.is_must_change_password:
            subject = "Bienvenue sur ROBERP"
            body = render_to_string("accounts/first_connexion_infos.html", {
                "user": user,
                "default_password": default_password
            })
        else:
            return "", "", ""  # Pas d'email par défaut
        employee = user.get_employee_in_company()
        return employee.email if employee and employee.email else user.email, subject, body
    except Exception as e:
        raise e



