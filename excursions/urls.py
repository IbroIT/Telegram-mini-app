from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.ExcursionCategoryViewSet, basename='excursion-category')
router.register(r'features', views.ExcursionFeatureViewSet, basename='excursion-feature')
router.register(r'excursions', views.ExcursionViewSet, basename='excursion')
router.register(r'bookings', views.ExcursionBookingViewSet, basename='excursion-booking')

urlpatterns = [
    path('', include(router.urls)),
    path('available-excursions/', views.AvailableExcursionsView.as_view(), name='available-excursions'),
    path('excursion-availability/<int:excursion_id>/', views.ExcursionAvailabilityView.as_view(), name='excursion-availability'),
    path('excursion-booking-calendar/', views.ExcursionBookingCalendarView.as_view(), name='excursion-booking-calendar'),
]