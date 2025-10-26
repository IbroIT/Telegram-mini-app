from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, DeliveryZoneViewSet, RentalProviderViewSet, ActiveServiceTermsView

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'delivery-zones', DeliveryZoneViewSet, basename='delivery-zone')
router.register(r'providers', RentalProviderViewSet, basename='provider')

urlpatterns = [
    path('', include(router.urls)),
    path('service-terms/', ActiveServiceTermsView.as_view(), name='service-terms'),
]
