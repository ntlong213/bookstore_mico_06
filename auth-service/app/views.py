from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
import hashlib, jwt, datetime, os

SECRET_KEY = os.environ.get('JWT_SECRET', 'bookstore-secret-2024')

# ── Helper functions ──────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user):
    payload = {
        'user_id':  user.id,
        'username': user.username,
        'role':     user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# ── Views ─────────────────────────────────────────────

class RegisterView(APIView):
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)

        data = s.validated_data

        if User.objects.filter(username=data['username']).exists():
            return Response({"error": "Username already exists"}, status=400)
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=data['role'],
        )
        token = generate_token(user)
        return Response({
            "message": "Registered successfully",
            "token": token,
            "user": UserSerializer(user).data
        }, status=201)


class LoginView(APIView):
    def post(self, request):
        s = LoginSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)

        data = s.validated_data
        try:
            user = User.objects.get(
                username=data['username'],
                password_hash=hash_password(data['password'])
            )
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=401)

        if not user.is_active:
            return Response({"error": "Account is disabled"}, status=403)

        token = generate_token(user)
        return Response({
            "message": "Login successful",
            "token": token,
            "user": UserSerializer(user).data
        })


class ValidateTokenView(APIView):
    """API Gateway gọi endpoint này để xác thực token"""
    def post(self, request):
        token = request.data.get('token', '')
        if not token:
            return Response({"valid": False, "error": "No token provided"}, status=400)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return Response({"valid": True, "payload": payload})
        except jwt.ExpiredSignatureError:
            return Response({"valid": False, "error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"valid": False, "error": "Invalid token"}, status=401)


class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


class ProfileView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            return Response(UserSerializer(user).data)
        except Exception as e:
            return Response({"error": str(e)}, status=401)