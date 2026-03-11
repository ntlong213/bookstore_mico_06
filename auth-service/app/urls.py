from django.urls import path
from .views import RegisterView, LoginView, ValidateTokenView, UserListView, ProfileView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/',    LoginView.as_view()),
    path('auth/validate/', ValidateTokenView.as_view()),
    path('auth/users/',    UserListView.as_view()),
    path('auth/profile/',  ProfileView.as_view()),
]