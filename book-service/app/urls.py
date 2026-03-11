from django.urls import path
from .views import BookListCreate, BookDetail, BookUpdateStock

urlpatterns = [
    path('books/', BookListCreate.as_view()),
    path('books/<int:pk>/', BookDetail.as_view()),
    path('books/<int:pk>/update-stock/', BookUpdateStock.as_view()),
]