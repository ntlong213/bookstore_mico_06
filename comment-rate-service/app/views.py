from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CommentRate
from .serializers import CommentRateSerializer
from django.db.models import Avg
from django.utils import timezone

class CommentRateListCreate(APIView):
    def get(self, request):
        book_id = request.query_params.get('book_id')
        qs = CommentRate.objects.filter(book_id=book_id) if book_id else CommentRate.objects.all()
        return Response(CommentRateSerializer(qs, many=True).data)

    def post(self, request):
        data = request.data.copy()
        if data.get('content') and not data.get('comment'):
            data['comment'] = data.get('content')

        payload = getattr(request, 'user_payload', {}) or {}
        if not data.get('customer_id'):
            data['customer_id'] = payload.get('user_id')

        s = CommentRateSerializer(data=data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentReplyView(APIView):
    def post(self, request, comment_id):
        payload = getattr(request, 'user_payload', {}) or {}
        role = payload.get('role')
        if role not in ['staff', 'manager']:
            return Response({'error': 'Only staff/manager can reply'}, status=status.HTTP_403_FORBIDDEN)

        reply = (request.data.get('reply') or '').strip()
        if not reply:
            return Response({'reply': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        obj = get_object_or_404(CommentRate, id=comment_id)
        obj.reply = reply
        obj.replied_by = payload.get('username') or str(payload.get('user_id') or '')
        obj.replied_at = timezone.now()
        obj.save(update_fields=['reply', 'replied_by', 'replied_at'])
        return Response(CommentRateSerializer(obj).data)

class BookRatingSummary(APIView):
    def get(self, request, book_id):
        avg = CommentRate.objects.filter(book_id=book_id).aggregate(Avg('rating'))
        count = CommentRate.objects.filter(book_id=book_id).count()
        return Response({
            "book_id": book_id,
            "average_rating": avg['rating__avg'],
            "total_reviews": count
        })