from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

from .models import MotoCategory, MotoFeature, Motorcycle, MotoBooking, MotoBrand
from .serializers import MotoCategorySerializer, MotoFeatureSerializer, MotorcycleSerializer, MotoBookingSerializer, CreateMotoBookingSerializer, MotorcycleListSerializer, MotoBrandSerializer

class MotoCategoryViewSet(viewsets.ModelViewSet):
    queryset = MotoCategory.objects.all()
    serializer_class = MotoCategorySerializer

class MotoBrandsView(APIView):
    """API для получения марок мотоциклов"""
    
    def get(self, request):
        brands = MotoBrand.objects.all()
        serializer = MotoBrandSerializer(brands, many=True, context={'request': request})
        return Response(serializer.data)

class MotoFeatureViewSet(viewsets.ModelViewSet):
    queryset = MotoFeature.objects.all()
    serializer_class = MotoFeatureSerializer

class MotorcycleViewSet(viewsets.ModelViewSet):
    queryset = Motorcycle.objects.all()
    serializer_class = MotorcycleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'oil_type', 'features', 'bike_type']
    search_fields = ['title', 'description', 'color', 'transmission', 'bike_type']
    ordering_fields = ['price_per_day', 'year', 'mileage', 'power', 'created_at']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Проверка доступности мотоцикла на определенные даты"""
        motorcycle = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Проверяем есть ли пересекающиеся бронирования
                conflicting_bookings = MotoBooking.objects.filter(
                    motorcycle=motorcycle,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and motorcycle.status == 'available'
                
                return Response({
                    'motorcycle_id': motorcycle.id,
                    'motorcycle_title': motorcycle.title,
                    'is_available': is_available,
                    'bookings': MotoBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
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

class MotoBookingViewSet(viewsets.ModelViewSet):
    queryset = MotoBooking.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMotoBookingSerializer
        return MotoBookingSerializer
    
    def get_queryset(self):
        # Для администраторов показываем все бронирования
        if self.request.user.is_staff:
            return MotoBooking.objects.all()
        # Для обычных запросов можно добавить фильтрацию по telegram_id если нужно
        return MotoBooking.objects.all()
    
    def perform_create(self, serializer):
        # Сохраняем без проверки пользователя
        serializer.save()

class AvailableMotorcyclesView(APIView):
    """Получение списка доступных мотоциклов"""
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        motorcycles = Motorcycle.objects.filter(status='available')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Исключаем мотоциклы с бронированиями на эти даты
                booked_moto_ids = MotoBooking.objects.filter(
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                ).values_list('motorcycle_id', flat=True)
                
                motorcycles = motorcycles.exclude(id__in=booked_moto_ids)
                
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = MotorcycleSerializer(motorcycles, many=True)
        return Response(serializer.data)

class MotoAvailabilityView(APIView):
    """Проверка доступности конкретного мотоцикла"""
    
    def get(self, request, motorcycle_id):
        try:
            motorcycle = Motorcycle.objects.get(id=motorcycle_id)
        except Motorcycle.DoesNotExist:
            return Response(
                {'error': 'Мотоцикл не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Проверяем конфликтующие бронирования
                conflicting_bookings = MotoBooking.objects.filter(
                    motorcycle=motorcycle,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and motorcycle.status == 'available'
                
                return Response({
                    'motorcycle_id': motorcycle.id,
                    'motorcycle_title': motorcycle.title,
                    'is_available': is_available,
                    'bookings': MotoBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
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

class MotoBookingCalendarView(APIView):
    """Получение данных для календаря бронирований мотоциклов"""
    
    def get(self, request):
        motorcycle_id = request.query_params.get('motorcycle_id')
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
            bookings_query = MotoBooking.objects.filter(
                status__in=['confirmed', 'active', 'pending'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            
            if motorcycle_id:
                motorcycle_id = int(motorcycle_id)
                bookings_query = bookings_query.filter(motorcycle_id=motorcycle_id)
            
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
                            'motorcycle': booking.motorcycle.title,
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
                    'motorcycle_id': booking.motorcycle.id,
                    'motorcycle_title': booking.motorcycle.title,
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
                'motorcycle_id': motorcycle_id
            })
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Неверный формат месяца или года: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

class MotorcycleCardsView(APIView):
    """API для получения всех мотоциклов в формате карточек"""
    
    def get(self, request):
        motorcycles = Motorcycle.objects.filter(status='available')
        serializer = MotorcycleListSerializer(
            motorcycles, 
            many=True, 
            context={'request': request}
        )
        return Response({
            'count': motorcycles.count(),
            'results': serializer.data
        })

class MotoCategoriesView(APIView):
    """API для получения категорий мотоциклов"""
    
    def get(self, request):
        categories = MotoCategory.objects.all()
        serializer = MotoCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class MotoFeaturesView(APIView):
    """API для получения особенностей мотоциклов"""
    
    def get(self, request):
        features = MotoFeature.objects.all()
        serializer = MotoFeatureSerializer(features, many=True)
        return Response(serializer.data)