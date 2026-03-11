from django.urls import path
from .views import StartOrderSaga, SagaStatusView, SagaListView

urlpatterns = [
    path('saga/order/', StartOrderSaga.as_view()),
    path('saga/<int:saga_id>/', SagaStatusView.as_view()),
    path('saga/', SagaListView.as_view()),
]