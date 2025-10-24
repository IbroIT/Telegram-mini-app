from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'features', views.FeatureViewSet, basename='feature')
router.register(r'cars', views.CarViewSet, basename='car')
router.register(r'bookings', views.BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('available-cars/', views.AvailableCarsView.as_view(), name='available-cars'),
    path('car-availability/<int:car_id>/', views.CarAvailabilityView.as_view(), name='car-availability'),
    path('booking-calendar/', views.BookingCalendarView.as_view(), name='booking-calendar'),
]