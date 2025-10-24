from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.HouseCategoryViewSet, basename='house-category')
router.register(r'features', views.HouseFeatureViewSet, basename='house-feature')
router.register(r'houses', views.HouseViewSet, basename='house')
router.register(r'bookings', views.HouseBookingViewSet, basename='house-booking')

urlpatterns = [
    path('', include(router.urls)),
    path('available-houses/', views.AvailableHousesView.as_view(), name='available-houses'),
    path('house-availability/<int:house_id>/', views.HouseAvailabilityView.as_view(), name='house-availability'),
    path('house-booking-calendar/', views.HouseBookingCalendarView.as_view(), name='house-booking-calendar'),
    
    # Новые endpoints для карточек
    path('cards/', views.HouseCardsView.as_view(), name='house-cards'),
    path('categories/', views.HouseCategoriesView.as_view(), name='house-categories'),
    path('features/', views.HouseFeaturesView.as_view(), name='house-features'),
]