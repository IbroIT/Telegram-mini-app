from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

from .models import HouseCategory, HouseFeature, House, HouseBooking
from .serializers import HouseCategorySerializer, HouseFeatureSerializer, HouseSerializer, HouseBookingSerializer, CreateHouseBookingSerializer

class HouseCategoryViewSet(viewsets.ModelViewSet):
    queryset = HouseCategory.objects.all()
    serializer_class = HouseCategorySerializer

class HouseFeatureViewSet(viewsets.ModelViewSet):
    queryset = HouseFeature.objects.all()
    serializer_class = HouseFeatureSerializer

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'features', 'floors']
    search_fields = ['title', 'description']
    ordering_fields = ['price_per_day', 'area', 'floors', 'created_at']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Проверка доступности дома на определенные даты"""
        house = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Проверяем есть ли пересекающиеся бронирования
                conflicting_bookings = HouseBooking.objects.filter(
                    house=house,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and house.status == 'available'
                
                return Response({
                    'house_id': house.id,
                    'house_title': house.title,
                    'is_available': is_available,
                    'bookings': HouseBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
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

class HouseBookingViewSet(viewsets.ModelViewSet):
    queryset = HouseBooking.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateHouseBookingSerializer
        return HouseBookingSerializer
    
    def get_queryset(self):
        # Пользователь видит только свои бронирования
        if self.request.user.is_staff:
            return HouseBooking.objects.all()
        return HouseBooking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Пользователь автоматически определяется из запроса
        serializer.save()

class AvailableHousesView(APIView):
    """Получение списка доступных домов"""
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        houses = House.objects.filter(status='available')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Исключаем дома с бронированиями на эти даты
                booked_house_ids = HouseBooking.objects.filter(
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                ).values_list('house_id', flat=True)
                
                houses = houses.exclude(id__in=booked_house_ids)
                
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)

class HouseAvailabilityView(APIView):
    """Проверка доступности конкретного дома"""
    
    def get(self, request, house_id):
        try:
            house = House.objects.get(id=house_id)
        except House.DoesNotExist:
            return Response(
                {'error': 'Дом не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Проверяем конфликтующие бронирования
                conflicting_bookings = HouseBooking.objects.filter(
                    house=house,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and house.status == 'available'
                
                return Response({
                    'house_id': house.id,
                    'house_title': house.title,
                    'is_available': is_available,
                    'bookings': HouseBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
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

class HouseBookingCalendarView(APIView):
    """Получение данных для календаря бронирований домов"""
    
    def get(self, request):
        house_id = request.query_params.get('house_id')
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
            bookings_query = HouseBooking.objects.filter(
                status__in=['confirmed', 'active', 'pending'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            
            if house_id:
                house_id = int(house_id)
                bookings_query = bookings_query.filter(house_id=house_id)
            
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
                            'house': booking.house.title,
                            'user': booking.user.username,
                            'status': booking.status,
                            'period': f"{booking.start_date} - {booking.end_date}",
                            'total_days': (booking.end_date - booking.start_date).days + 1,
                            'guests': booking.guests
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
                    'house_id': booking.house.id,
                    'house_title': booking.house.title,
                    'start_date': booking.start_date,
                    'end_date': booking.end_date,
                    'status': booking.status,
                    'user': booking.user.username,
                    'period': f"{booking.start_date} - {booking.end_date}",
                    'total_days': (booking.end_date - booking.start_date).days + 1,
                    'guests': booking.guests
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
                'house_id': house_id
            })
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Неверный формат месяца или года: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )