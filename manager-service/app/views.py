from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Manager
from .serializers import ManagerSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
STAFF_SERVICE_URL = "http://staff-service:8000"

class ManagerListCreate(APIView):
    def get(self, request):
        managers = Manager.objects.all()
        return Response(ManagerSerializer(managers, many=True).data)

    def post(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ManagerStaffOverview(APIView):
    """Manager xem danh sách staff"""
    def get(self, request):
        try:
            r = requests.get(f"{STAFF_SERVICE_URL}/staff/", timeout=5)
            return Response({"staff": r.json()})
        except Exception as e:
            return Response({"error": str(e)}, status=503)