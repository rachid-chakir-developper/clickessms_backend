from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_this_email(subject, html_content, to_email, from_name="Roberp Support", from_email=settings.DEFAULT_FROM_EMAIL, reply_to_email=None):
    """
    Envoie un email avec un contenu HTML et une alternative en texte brut.
    
    :param subject: Sujet de l'email
    :param html_content: Contenu HTML de l'email
    :param from_email: Adresse email de l'expéditeur
    :param to_email: Liste des destinataires (ex: ["test@example.com"])
    :param reply_to_email: Adresse email où les réponses doivent être envoyées (ex: ["support@example.com"])
    :return: True si l'email est envoyé avec succès, False sinon
    """
    try:
        # Création de l'email avec alternative texte brut
        full_from_email = f"{from_name} <{from_email}>"
        email = EmailMultiAlternatives(
            subject=subject,
            body="Votre client email ne supporte pas les emails HTML.",
            from_email=full_from_email,
            to=to_email,
            reply_to=reply_to_email if reply_to_email else [from_email],  # Ajout du Reply-To
        )
        email.attach_alternative(html_content, "text/html")

        # Envoi de l'email
        email.send()
        return True  # Email envoyé avec succès
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False
