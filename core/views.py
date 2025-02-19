from rest_framework import viewsets


from core.models import City
from core.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
