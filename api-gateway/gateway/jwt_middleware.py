import jwt
import os
from django.http import JsonResponse

SECRET_KEY = os.environ.get('JWT_SECRET', 'bookstore-secret-2024')

PUBLIC_PATHS = [
    '/auth/login/',
    '/auth/register/',
    '/login/',
    '/customers/new/',
    '/',
    '/health/',
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
        # Bỏ qua public paths - cho phép mọi method
        if any(request.path.startswith(p) for p in PUBLIC_PATHS):
            return self.get_response(request)  # ← bỏ check method GET

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