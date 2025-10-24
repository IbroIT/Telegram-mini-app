from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

from .models import Category, Feature, Car, Booking
from .serializers import CategorySerializer, FeatureSerializer, CarSerializer, BookingSerializer, CreateBookingSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'oil_type', 'features']
    search_fields = ['title', 'description', 'color', 'transmission']
    ordering_fields = ['price_per_day', 'year', 'mileage', 'created_at']

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer
    
    def get_queryset(self):
        # Для администраторов показываем все бронирования
        if self.request.user.is_staff:
            return Booking.objects.all()
        # Для обычных запросов можно добавить фильтрацию по telegram_id если нужно
        return Booking.objects.all()
    
    def perform_create(self, serializer):
        # Сохраняем без проверки пользователя
        serializer.save()

class AvailableCarsView(APIView):
    """Получение списка доступных автомобилей"""
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        cars = Car.objects.filter(status='available')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Исключаем автомобили с бронированиями на эти даты
                booked_car_ids = Booking.objects.filter(
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                ).values_list('car_id', flat=True)
                
                cars = cars.exclude(id__in=booked_car_ids)
                
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

class CarAvailabilityView(APIView):
    """Проверка доступности конкретного автомобиля"""
    
    def get(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(
                {'error': 'Автомобиль не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Проверяем конфликтующие бронирования
                conflicting_bookings = Booking.objects.filter(
                    car=car,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and car.status == 'available'
                
                return Response({
                    'car_id': car.id,
                    'car_title': car.title,
                    'is_available': is_available,
                    'bookings': BookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
                    'message': 'Свободен' if is_available else 'Занят на указанные даты'
                })
                
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'error': 'Необходимо указать start_date и end_date'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class BookingCalendarView(APIView):
    """Получение данных для календаря бронирований с отображением периодов"""
    
    def get(self, request):
        car_id = request.query_params.get('car_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        try:
            if month and year:
                target_month = int(month)
                target_year = int(year)
                start_date = datetime(target_year, target_month, 1).date()
                if target_month == 12:
                    end_date = datetime(target_year + 1, 1, 1).date()
                else:
                    end_date = datetime(target_year, target_month + 1, 1).date()
            else:
                # По умолчанию текущий месяц
                today = timezone.now().date()
                start_date = datetime(today.year, today.month, 1).date()
                if today.month == 12:
                    end_date = datetime(today.year + 1, 1, 1).date()
                else:
                    end_date = datetime(today.year, today.month + 1, 1).date()
            
            # Получаем бронирования
            bookings_query = Booking.objects.filter(
                status__in=['confirmed', 'active', 'pending'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            
            if car_id:
                car_id = int(car_id)
                bookings_query = bookings_query.filter(car_id=car_id)
            
            # Создаем календарь с периодами бронирования
            calendar_data = []
            current_date = start_date
            
            while current_date < end_date:
                # Находим бронирования на эту дату
                date_bookings = []
                for booking in bookings_query:
                    if booking.start_date <= current_date <= booking.end_date:
                        date_bookings.append({
                            'id': booking.id,
                            'car': booking.car.title,
                            'user': booking.user.username,
                            'status': booking.status,
                            'period': f"{booking.start_date} - {booking.end_date}",
                            'total_days': (booking.end_date - booking.start_date).days + 1
                        })
                
                is_available = len(date_bookings) == 0
                
                calendar_data.append({
                    'date': current_date,
                    'is_available': is_available,
                    'bookings': date_bookings
                })
                
                current_date += timedelta(days=1)
            
            # Группируем занятые периоды для удобного отображения
            booked_periods = []
            for booking in bookings_query:
                booked_periods.append({
                    'id': booking.id,
                    'car_id': booking.car.id,
                    'car_title': booking.car.title,
                    'start_date': booking.start_date,
                    'end_date': booking.end_date,
                    'status': booking.status,
                    'user': booking.user.username,
                    'period': f"{booking.start_date} - {booking.end_date}",
                    'total_days': (booking.end_date - booking.start_date).days + 1
                })
            
            return Response({
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'month': start_date.month,
                    'year': start_date.year
                },
                'calendar': calendar_data,
                'booked_periods': booked_periods,
                'car_id': car_id
            })
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Неверный формат месяца или года: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )