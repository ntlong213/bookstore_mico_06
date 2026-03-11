from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"

class OrderListCreate(APIView):
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        orders = Order.objects.filter(customer_id=customer_id) if customer_id else Order.objects.all()
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        customer_id = request.data.get('customer_id')
        payment_method = request.data.get('payment_method', 'cash')
        shipping_address = request.data.get('shipping_address', '')

        # Lấy cart của customer
        try:
            cart_r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/", timeout=5)
            cart_data = cart_r.json()
            cart_items = cart_data.get('items', [])
        except Exception:
            return Response({"error": "Cart service unavailable"}, status=503)

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=400)

        # Tính total
        total = sum(float(item.get('price_at_add', 0)) * item['quantity'] for item in cart_items)

        # Tạo order
        order = Order.objects.create(
            customer_id=customer_id,
            total_amount=total,
            payment_method=payment_method,
            shipping_address=shipping_address
        )

        # Tạo order items & cập nhật stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book_id=item['book_id'],
                quantity=item['quantity'],
                price=item.get('price_at_add', 0)
            )
            # Giảm stock
            try:
                requests.post(
                    f"{BOOK_SERVICE_URL}/books/{item['book_id']}/update-stock/",
                    json={"quantity": item['quantity']},
                    timeout=5
                )
            except:
                pass

        # Trigger payment
        try:
            requests.post(f"{PAY_SERVICE_URL}/payments/", json={
                "order_id": order.id,
                "amount": str(total),
                "method": payment_method
            }, timeout=5)
        except:
            pass

        # Trigger shipping
        try:
            requests.post(f"{SHIP_SERVICE_URL}/shipments/", json={
                "order_id": order.id,
                "address": shipping_address
            }, timeout=5)
        except:
            pass

        order.status = 'confirmed'
        order.save()

        return Response(OrderSerializer(order).data, status=201)

class OrderDetail(APIView):
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get('status')
            if new_status:
                order.status = new_status
                order.save()
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({"error": "Not found"}, status=404)