from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

class CartCreate(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(CartSerializer(cart).data, status=201 if created else 200)

class CartByCustomer(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        cart_id = request.data.get("cart_id")
        quantity = request.data.get("quantity", 1)

        # Validate book tồn tại
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5)
            if r.status_code == 404:
                return Response({"error": "Book not found"}, status=400)
            book = r.json()
        except Exception:
            return Response({"error": "Book service unavailable"}, status=503)

        # Thêm hoặc cập nhật item
        try:
            cart = Cart.objects.get(id=cart_id)
            item, created = CartItem.objects.get_or_create(
                cart=cart, book_id=book_id,
                defaults={'quantity': quantity, 'price_at_add': book.get('price')}
            )
            if not created:
                item.quantity += quantity
                item.save()
            return Response(CartItemSerializer(item).data, status=201)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

class UpdateCartItem(APIView):
    def put(self, request, item_id):
        try:
            item = CartItem.objects.get(pk=item_id)
            quantity = request.data.get('quantity')
            if quantity is not None:
                if quantity <= 0:
                    item.delete()
                    return Response({"message": "Item removed"})
                item.quantity = quantity
                item.save()
            return Response(CartItemSerializer(item).data)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

class RemoveCartItem(APIView):
    def delete(self, request, item_id):
        try:
            CartItem.objects.get(pk=item_id).delete()
            return Response(status=204)
        except CartItem.DoesNotExist:
            return Response({"error": "Not found"}, status=404)