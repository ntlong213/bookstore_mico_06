from django.urls import path

from .views import PaymentConfirm, PaymentListCreate


urlpatterns = [
    path('payments/', PaymentListCreate.as_view(), name='payments_list_create'),
    path('payments/<int:pk>/confirm/', PaymentConfirm.as_view(), name='payments_confirm'),
]
