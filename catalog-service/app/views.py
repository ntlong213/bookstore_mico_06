from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, CatalogEntry
from .serializers import CategorySerializer, CatalogEntrySerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

class CategoryListCreate(APIView):
    def get(self, request):
        cats = Category.objects.all()
        return Response(CategorySerializer(cats, many=True).data)

    def post(self, request):
        s = CategorySerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)

class CatalogListCreate(APIView):
    def get(self, request):
        entries = CatalogEntry.objects.all()
        # Enrich với book data
        result = []
        try:
            books_r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
            books = {b['id']: b for b in books_r.json()}
        except:
            books = {}
        for entry in entries:
            data = CatalogEntrySerializer(entry).data
            data['book'] = books.get(entry.book_id, {})
            result.append(data)
        return Response(result)

    def post(self, request):
        s = CatalogEntrySerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)