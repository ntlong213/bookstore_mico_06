from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer
import uuid

class ShipmentListCreate(APIView):
    def get(self, request):
        order_id = request.query_params.get('order_id')
        shipments = Shipment.objects.filter(order_id=order_id) if order_id else Shipment.objects.all()
        return Response(ShipmentSerializer(shipments, many=True).data)

    def post(self, request):
        s = ShipmentSerializer(data=request.data)
        if s.is_valid():
            shipment = s.save()
            # Tự sinh tracking number
            shipment.tracking_number = str(uuid.uuid4())[:12].upper()
            shipment.save()
            return Response(ShipmentSerializer(shipment).data, status=201)
        return Response(s.errors, status=400)

class ShipmentUpdateStatus(APIView):
    def put(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
            shipment.status = request.data.get('status', shipment.status)
            shipment.save()
            return Response(ShipmentSerializer(shipment).data)
        except Shipment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)