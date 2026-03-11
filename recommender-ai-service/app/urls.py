from django.urls import path
from .views import RecommendBooks

urlpatterns = [
    path('recommend/<int:customer_id>/', RecommendBooks.as_view()),
]