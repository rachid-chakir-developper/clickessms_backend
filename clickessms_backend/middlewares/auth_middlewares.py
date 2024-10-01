from graphql_jwt.utils import jwt_decode
from django.contrib.auth import get_user_model
from graphql_jwt.exceptions import JSONWebTokenError
from django.http import HttpResponse

User = get_user_model()

def inject_user_from_jwt_sync(request, token):
    try:
        # Décoder le token JWT
        decoded_data = jwt_decode(token)
        
        # Récupérer l'utilisateur à partir du nom d'utilisateur décodé
        username = decoded_data.get('username')
        if not username:
            return HttpResponse("Le token JWT n'inclut pas de nom d'utilisateur", status=401)

        # Chercher l'utilisateur dans la base de données (méthode synchrone)
        user = User.objects.get(username=username)

        # Injecter l'utilisateur dans la requête
        request.user = user
    except User.DoesNotExist:
        return HttpResponse("Utilisateur non trouvé", status=404)
    except JSONWebTokenError:
        return HttpResponse("Le token JWT est invalide ou expiré", status=401)
    except Exception as e:
        return HttpResponse(f"Erreur lors de la récupération de l'utilisateur : {str(e)}", status=500)
    
    return None  # Retourne None si tout s'est bien passé


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('JWT '):
            token = auth_header.split(' ')[1]
            
            # Injecter l'utilisateur avec le token JWT de manière synchrone
            response = inject_user_from_jwt_sync(request, token)
            if response:  # Si la fonction retourne une réponse HTTP (erreur), on la retourne immédiatement
                return response

        # Si pas de token ou token invalide, l'utilisateur reste non authentifié
        response = self.get_response(request)
        return response
