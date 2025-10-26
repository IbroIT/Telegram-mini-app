from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import City, DeliveryZone, RentalProvider, ServiceTerms
from .serializers import CitySerializer, DeliveryZoneSerializer, RentalProviderSerializer, ServiceTermsSerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения городов"""
    queryset = City.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = CitySerializer


class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения зон доставки"""
    queryset = DeliveryZone.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = DeliveryZoneSerializer


class RentalProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения прокатчиков"""
    queryset = RentalProvider.objects.filter(is_active=True)
    serializer_class = RentalProviderSerializer


class ActiveServiceTermsView(APIView):
    """API для получения активных условий обслуживания"""
    
    def get(self, request):
        active_terms = ServiceTerms.get_active_terms()
        serializer = ServiceTermsSerializer(active_terms, many=True)
        return Response(serializer.data)
