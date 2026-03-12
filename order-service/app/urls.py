from django.urls import path

from .views import OrderDetail, OrderListCreate


urlpatterns = [
    path('orders/', OrderListCreate.as_view(), name='orders_list_create'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='orders_detail'),
]
