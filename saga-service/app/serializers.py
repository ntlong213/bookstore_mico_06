from rest_framework import serializers
from .models import SagaTransaction

class SagaTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaTransaction
        fields = '__all__'
