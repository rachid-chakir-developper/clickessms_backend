import jwt
from django.conf import settings
from django.utils.timezone import now

def decode_access_token(access_token):
    """
    Décode un token JWT et vérifie son expiration.
    Retourne tout le payload si valide, sinon lève une ValueError.
    """
    try:
        # Décodage du token
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

        # Vérification de l'expiration du token
        if payload.get("exp") and now().timestamp() > payload["exp"]:
            raise ValueError("Le token a expiré.")

        return payload  # Retourne tout le payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Le token a expiré.")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalide.")
