from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SagaTransaction
from .saga_orchestrator import OrderSaga
from .serializers import SagaTransactionSerializer

class StartOrderSaga(APIView):
    def post(self, request):
        saga = SagaTransaction.objects.create(
            order_id=0,
            customer_id=request.data.get('customer_id', 0)
        )
        orchestrator = OrderSaga(saga)
        result = orchestrator.execute(request.data)
        if result['success']:
            return Response(result, status=201)
        return Response(result, status=500)

class SagaStatusView(APIView):
    def get(self, request, saga_id):
        try:
            saga = SagaTransaction.objects.get(pk=saga_id)
            return Response(SagaTransactionSerializer(saga).data)
        except SagaTransaction.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

class SagaListView(APIView):
    def get(self, request):
        sagas = SagaTransaction.objects.all().order_by('-created_at')
        return Response(SagaTransactionSerializer(sagas, many=True).data)