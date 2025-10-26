from rest_framework import serializers
from .models import ExcursionCategory, ExcursionFeature, Excursion, ExcursionImage, ExcursionBooking, ExcursionPriceTier
from core.serializers import CitySerializer, DeliveryZoneSerializer, RentalProviderSerializer

class ExcursionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionCategory
        fields = ['id', 'title', 'icon']

class ExcursionFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionFeature
        fields = ['id', 'title']

class ExcursionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'order']


class ExcursionPriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionPriceTier
        fields = ['id', 'min_participants', 'price_per_person', 'is_active']


class ExcursionSerializer(serializers.ModelSerializer):
    images = ExcursionImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = ExcursionFeatureSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    rental_provider = RentalProviderSerializer(read_only=True)
    delivery_zones = DeliveryZoneSerializer(many=True, read_only=True)
    price_tiers = ExcursionPriceTierSerializer(many=True, read_only=True)
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'days', 'price_per_person', 'deposit', 'status', 'features', 'images', 
            'city', 'rental_provider', 'delivery_zones', 'price_tiers', 'created_at'
        ]

class ExcursionBookingSerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    city = CitySerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    provider_terms = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcursionBooking
        fields = [
            'id', 'excursion', 'excursion_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'participants', 'status', 'city', 'delivery_zone', 
            'excursion_price', 'transfer_price', 'deposit', 'total_price',
            'provider_terms_accepted', 'service_terms_accepted', 'provider_terms',
            'comment', 'created_at'
        ]
        read_only_fields = ['excursion_price', 'transfer_price', 'deposit', 'total_price', 'status', 'total_days']
    
    def get_provider_terms(self, obj):
        """Получить правила организатора для данной брони"""
        if obj.excursion and obj.excursion.rental_provider:
            return obj.excursion.rental_provider.terms
        return None


class CreateExcursionBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionBooking
        fields = [
            'excursion', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'participants', 'city', 'delivery_zone',
            'provider_terms_accepted', 'service_terms_accepted', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
        # Проверка согласия с правилами
        if not data.get('provider_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами организатора")
        
        if not data.get('service_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами сервиса")
        
        excursion = data['excursion']
        conflicting_bookings = ExcursionBooking.objects.filter(
            excursion=excursion,
            status__in=['confirmed', 'active', 'pending'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("На выбранные даты экскурсия уже забронирована")
        
        return data
    
    def create(self, validated_data):
        booking = ExcursionBooking.objects.create(**validated_data)
        return booking
    
class ExcursionListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка экскурсий (карточек)"""
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = ExcursionFeatureSerializer(many=True, read_only=True)
    first_image = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)
    price_for_participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'category_title', 'days', 'price_per_person',
            'status', 'features', 'first_image', 'city', 'price_for_participants'
        ]
    
    def get_first_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None
    
    def get_price_for_participants(self, obj):
        """Возвращает расчет цен для разного количества участников"""
        return {
            '1_person': obj.get_price_for_participants(1),
            '2_persons': obj.get_price_for_participants(2),
            '5_persons': obj.get_price_for_participants(5),
            '10_persons': obj.get_price_for_participants(10),
        }