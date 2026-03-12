from django.urls import path

from .views import ShipmentListCreate, ShipmentUpdateStatus


urlpatterns = [
    path('shipments/', ShipmentListCreate.as_view(), name='shipments_list_create'),
    path('shipments/<int:pk>/', ShipmentUpdateStatus.as_view(), name='shipments_update_status'),
]
