from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CommentRate
from .serializers import CommentRateSerializer
from django.db.models import Avg

class CommentRateListCreate(APIView):
    def get(self, request):
        book_id = request.query_params.get('book_id')
        qs = CommentRate.objects.filter(book_id=book_id) if book_id else CommentRate.objects.all()
        return Response(CommentRateSerializer(qs, many=True).data)

    def post(self, request):
        s = CommentRateSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)

class BookRatingSummary(APIView):
    def get(self, request, book_id):
        avg = CommentRate.objects.filter(book_id=book_id).aggregate(Avg('rating'))
        count = CommentRate.objects.filter(book_id=book_id).count()
        return Response({
            "book_id": book_id,
            "average_rating": avg['rating__avg'],
            "total_reviews": count
        })