from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from django.utils import timezone

class PaymentListCreate(APIView):
    def get(self, request):
        order_id = request.query_params.get('order_id')
        payments = Payment.objects.filter(order_id=order_id) if order_id else Payment.objects.all()
        return Response(PaymentSerializer(payments, many=True).data)

    def post(self, request):
        s = PaymentSerializer(data=request.data)
        if s.is_valid():
            payment = s.save()
            # Simulate payment success
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.save()
            return Response(PaymentSerializer(payment).data, status=201)
        return Response(s.errors, status=400)

class PaymentConfirm(APIView):
    def post(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.save()
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)