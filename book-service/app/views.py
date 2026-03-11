from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class BookListCreate(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class BookDetail(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            return Response(BookSerializer(book).data)
        except Book.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            s = BookSerializer(book, data=request.data, partial=True)
            if s.is_valid():
                s.save()
                return Response(s.data)
            return Response(s.errors, status=400)
        except Book.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

    def delete(self, request, pk):
        try:
            Book.objects.get(pk=pk).delete()
            return Response(status=204)
        except Book.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

class BookUpdateStock(APIView):
    """Dùng bởi order-service để trừ stock"""
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            quantity = request.data.get('quantity', 1)
            if book.stock < quantity:
                return Response({"error": "Insufficient stock"}, status=400)
            book.stock -= quantity
            book.save()
            return Response({"message": "Stock updated", "new_stock": book.stock})
        except Book.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
    
    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            quantity = int(request.data.get('quantity', 0))
            book.stock += quantity
            book.save()
            return Response({"message": "Stock updated", "new_stock": book.stock})
        except Book.DoesNotExist:
            return Response({"error": "Not found"}, status=404)