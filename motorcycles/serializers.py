from rest_framework import serializers
from .models import MotoCategory, MotoFeature, Motorcycle, MotoImage, MotoBooking, MotoBrand, MotoModel, MotoPriceTier
from core.serializers import CitySerializer, DeliveryZoneSerializer, RentalProviderSerializer

class MotoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoCategory
        fields = ['id', 'title', 'icon']

class MotoFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoFeature
        fields = ['id', 'title']

class MotoImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoImage
        fields = ['id', 'image', 'order']


class MotoPriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoPriceTier
        fields = ['id', 'min_days', 'price_per_day', 'is_active']


class MotorcycleSerializer(serializers.ModelSerializer):
    images = MotoImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = MotoFeatureSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    rental_provider = RentalProviderSerializer(read_only=True)
    delivery_zones = DeliveryZoneSerializer(many=True, read_only=True)
    price_tiers = MotoPriceTierSerializer(many=True, read_only=True)
    
    class Meta:
        model = Motorcycle
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'year', 'color', 'engine_volume', 'mileage', 'transmission',
            'oil_type', 'bike_type', 'power', 'price_per_day', 'deposit', 
            'status', 'features', 'images', 'city', 'rental_provider', 'delivery_zones',
            'price_tiers', 'created_at'
        ]

class MotoBookingSerializer(serializers.ModelSerializer):
    motorcycle_title = serializers.CharField(source='motorcycle.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    city = CitySerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    provider_terms = serializers.SerializerMethodField()
    
    class Meta:
        model = MotoBooking
        fields = [
            'id', 'motorcycle', 'motorcycle_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'city', 'delivery_zone', 
            'rental_price', 'delivery_price', 'deposit', 'total_price',
            'provider_terms_accepted', 'service_terms_accepted', 'provider_terms',
            'comment', 'created_at'
        ]
        read_only_fields = ['rental_price', 'delivery_price', 'deposit', 'total_price', 'status', 'total_days']
    
    def get_provider_terms(self, obj):
        """Получить правила прокатчика для данной брони"""
        if obj.motorcycle and obj.motorcycle.rental_provider:
            return obj.motorcycle.rental_provider.terms
        return None


class CreateMotoBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoBooking
        fields = [
            'motorcycle', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'city', 'delivery_zone',
            'provider_terms_accepted', 'service_terms_accepted', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
        # Проверка согласия с правилами
        if not data.get('provider_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами прокатчика")
        
        if not data.get('service_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами сервиса")
        
        motorcycle = data['motorcycle']
        conflicting_bookings = MotoBooking.objects.filter(
            motorcycle=motorcycle,
            status__in=['confirmed', 'active', 'pending'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("На выбранные даты мотоцикл уже забронирован")
        
        return data
    
    def create(self, validated_data):
        booking = MotoBooking.objects.create(**validated_data)
        return booking
    

class MotoBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoBrand
        fields = ['id', 'name', 'icon']

class MotorcycleListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка мотоциклов (карточек)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_icon = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = MotoFeatureSerializer(many=True, read_only=True)
    first_image = serializers.SerializerMethodField()
    price_per_day = serializers.IntegerField()
    
    class Meta:
        model = Motorcycle
        fields = [
            'id', 'title', 'brand', 'brand_name', 'brand_icon', 'category_title',
            'year', 'color', 'engine_volume', 'mileage', 'transmission', 'oil_type',
            'bike_type', 'power', 'price_per_day', 'deposit', 'status', 
            'features', 'first_image'
        ]
    
    def get_brand_icon(self, obj):
        if obj.brand and obj.brand.icon:
            return self.context['request'].build_absolute_uri(obj.brand.icon.url)
        return None
    
    def get_first_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None
    

class MotoModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = MotoModel
        fields = ['id', 'brand', 'brand_name', 'name', 'icon']
