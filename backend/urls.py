from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/cars/', include('cars.urls')),
    path('api/motorcycles/', include('motorcycles.urls')),
    path('api/houses/', include('houses.urls')),  
    path('api/excursions/', include('excursions.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Панель управления арендой автомобилей"
admin.site.site_title = "Админка аренды авто"
admin.site.index_title = "Добро пожаловать в систему управления арендой"