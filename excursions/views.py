from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

from .models import ExcursionCategory, ExcursionFeature, Excursion, ExcursionBooking
from .serializers import ExcursionCategorySerializer, ExcursionFeatureSerializer, ExcursionSerializer, ExcursionBookingSerializer, CreateExcursionBookingSerializer

class ExcursionCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExcursionCategory.objects.all()
    serializer_class = ExcursionCategorySerializer

class ExcursionFeatureViewSet(viewsets.ModelViewSet):
    queryset = ExcursionFeature.objects.all()
    serializer_class = ExcursionFeatureSerializer

class ExcursionViewSet(viewsets.ModelViewSet):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'features', 'days']
    search_fields = ['title', 'description']
    ordering_fields = ['price_per_person', 'days', 'created_at']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Проверка доступности экскурсии на определенные даты"""
        excursion = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if end <= start:
                    return Response({
                        'error': 'Дата окончания должна быть позже даты начала'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Проверяем есть ли пересекающиеся бронирования
                conflicting_bookings = ExcursionBooking.objects.filter(
                    excursion=excursion,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and excursion.status == 'available'
                
                return Response({
                    'excursion_id': excursion.id,
                    'excursion_title': excursion.title,
                    'is_available': is_available,
                    'bookings': ExcursionBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
                    'message': 'Доступна' if is_available else 'Недоступна на выбранные даты'
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

class ExcursionBookingViewSet(viewsets.ModelViewSet):
    queryset = ExcursionBooking.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateExcursionBookingSerializer
        return ExcursionBookingSerializer
    
    def get_queryset(self):
        # Пользователь видит только свои бронирования
        if self.request.user.is_staff:
            return ExcursionBooking.objects.all()
        return ExcursionBooking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Пользователь автоматически определяется из запроса (Telegram)
        serializer.save()

class AvailableExcursionsView(APIView):
    """Получение списка доступных экскурсий на определенные даты"""
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        excursions = Excursion.objects.filter(status='available')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if end <= start:
                    return Response(
                        {'error': 'Дата окончания должна быть позже даты начала'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                available_excursions = []
                for excursion in excursions:
                    # Проверяем доступность для каждой экскурсии
                    conflicting_bookings = ExcursionBooking.objects.filter(
                        excursion=excursion,
                        status__in=['confirmed', 'active', 'pending'],
                        start_date__lte=end,
                        end_date__gte=start
                    )
                    
                    if not conflicting_bookings.exists():
                        excursion_data = ExcursionSerializer(excursion).data
                        available_excursions.append(excursion_data)
                
                return Response(available_excursions)
                
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = ExcursionSerializer(excursions, many=True)
        return Response(serializer.data)

class ExcursionAvailabilityView(APIView):
    """Проверка доступности конкретной экскурсии на даты"""
    
    def get(self, request, excursion_id):
        try:
            excursion = Excursion.objects.get(id=excursion_id)
        except Excursion.DoesNotExist:
            return Response(
                {'error': 'Экскурсия не найдена'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if end <= start:
                    return Response({
                        'error': 'Дата окончания должна быть позже даты начала'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Проверяем конфликтующие бронирования
                conflicting_bookings = ExcursionBooking.objects.filter(
                    excursion=excursion,
                    status__in=['confirmed', 'active', 'pending'],
                    start_date__lte=end,
                    end_date__gte=start
                )
                
                is_available = not conflicting_bookings.exists() and excursion.status == 'available'
                
                return Response({
                    'excursion_id': excursion.id,
                    'excursion_title': excursion.title,
                    'is_available': is_available,
                    'bookings': ExcursionBookingSerializer(conflicting_bookings, many=True).data if not is_available else [],
                    'message': 'Доступна' if is_available else 'Недоступна на выбранные даты'
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

class ExcursionBookingCalendarView(APIView):
    """Получение данных для календаря бронирований экскурсий"""
    
    def get(self, request):
        excursion_id = request.query_params.get('excursion_id')
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
            bookings_query = ExcursionBooking.objects.filter(
                status__in=['confirmed', 'active', 'pending'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            
            if excursion_id:
                excursion_id = int(excursion_id)
                bookings_query = bookings_query.filter(excursion_id=excursion_id)
            
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
                            'excursion': booking.excursion.title,
                            'client_name': booking.client_name,
                            'user': booking.user.username,
                            'status': booking.status,
                            'period': f"{booking.start_date} - {booking.end_date}",
                            'total_days': booking.total_days,
                            'participants': booking.participants
                        })
                
                # Проверяем доступность для каждой экскурсии
                excursions_availability = []
                if excursion_id:
                    # Если указана конкретная экскурсия
                    try:
                        excursion = Excursion.objects.get(id=excursion_id)
                        is_available = not any(b['excursion'] == excursion.title for b in date_bookings)
                        excursions_availability.append({
                            'excursion_id': excursion.id,
                            'excursion_title': excursion.title,
                            'is_available': is_available
                        })
                    except Excursion.DoesNotExist:
                        pass
                else:
                    # Все экскурсии
                    excursions = Excursion.objects.filter(status='available')
                    for excursion in excursions:
                        is_available = not any(b['excursion'] == excursion.title for b in date_bookings)
                        excursions_availability.append({
                            'excursion_id': excursion.id,
                            'excursion_title': excursion.title,
                            'is_available': is_available
                        })
                
                calendar_data.append({
                    'date': current_date,
                    'bookings': date_bookings,
                    'excursions_availability': excursions_availability
                })
                
                current_date += timedelta(days=1)
            
            return Response({
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'month': start_date.month,
                    'year': start_date.year
                },
                'calendar': calendar_data,
                'excursion_id': excursion_id
            })
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Неверный формат месяца или года: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )