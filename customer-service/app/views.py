from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"

class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        return Response(CustomerSerializer(customers, many=True).data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            try:
                requests.post(f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": customer.id}, timeout=5)
            except:
                pass
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class CustomerDetail(APIView):
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            return Response(CustomerSerializer(customer).data)
        except Customer.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            s = CustomerSerializer(customer, data=request.data, partial=True)
            if s.is_valid():
                s.save()
                return Response(s.data)
            return Response(s.errors, status=400)
        except Customer.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

    def delete(self, request, pk):
        try:
            Customer.objects.get(pk=pk).delete()
            return Response(status=204)
        except Customer.DoesNotExist:
            return Response({"error": "Not found"}, status=404)