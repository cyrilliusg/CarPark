# views.py
from rest_framework import generics
from .models import Vehicle
from .serializers import VehicleSerializer

class VehicleListAPIView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
