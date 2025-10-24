from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.MotoCategoryViewSet, basename='moto-category')
router.register(r'features', views.MotoFeatureViewSet, basename='moto-feature')
router.register(r'motorcycles', views.MotorcycleViewSet, basename='motorcycle')
router.register(r'bookings', views.MotoBookingViewSet, basename='moto-booking')

urlpatterns = [
    path('', include(router.urls)),
    path('available-motorcycles/', views.AvailableMotorcyclesView.as_view(), name='available-motorcycles'),
    path('moto-availability/<int:motorcycle_id>/', views.MotoAvailabilityView.as_view(), name='moto-availability'),
    path('moto-booking-calendar/', views.MotoBookingCalendarView.as_view(), name='moto-booking-calendar'),
    
    # Новые endpoints для карточек
    path('cards/', views.MotorcycleCardsView.as_view(), name='motorcycle-cards'),
    path('categories/', views.MotoCategoriesView.as_view(), name='moto-categories'),
    path('brands/', views.MotoBrandsView.as_view(), name='moto-brands'),
    path('features/', views.MotoFeaturesView.as_view(), name='moto-features'),
]