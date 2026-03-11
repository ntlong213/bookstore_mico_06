import jwt
import os
from django.http import JsonResponse

SECRET_KEY = os.environ.get('JWT_SECRET', 'bookstore-secret-key-2024')

# Các endpoint không cần auth
PUBLIC_PATHS = [
    '/auth/login/',
    '/auth/register/',
    '/books/',       # GET public
]

ROLE_PERMISSIONS = {
    'customer': ['GET'],
    'staff':    ['GET', 'POST', 'PUT'],
    'manager':  ['GET', 'POST', 'PUT', 'DELETE'],
}

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bỏ qua public paths
        if any(request.path.startswith(p) for p in PUBLIC_PATHS):
            if request.method == 'GET':
                return self.get_response(request)

        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_payload = payload
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)