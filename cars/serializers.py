from rest_framework import serializers
from .models import Car, Booking, Category, Feature, CarImage, Brand, CarModel, PriceTier
from core.serializers import CitySerializer, DeliveryZoneSerializer, RentalProviderSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'icon']

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'title']

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'order']


class PriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTier
        fields = ['id', 'min_days', 'price_per_day', 'is_active']


class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    rental_provider = RentalProviderSerializer(read_only=True)
    delivery_zones = DeliveryZoneSerializer(many=True, read_only=True)
    price_tiers = PriceTierSerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'year', 'color', 'engine_volume', 'mileage', 'transmission',
            'oil_type', 'price_per_day', 'deposit', 'status',
            'features', 'images', 'city', 'rental_provider', 'delivery_zones',
            'price_tiers', 'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    car_title = serializers.CharField(source='car.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    city = CitySerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    provider_terms = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'car', 'car_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'city', 'delivery_zone', 
            'rental_price', 'delivery_price', 'deposit', 'total_price',
            'provider_terms_accepted', 'service_terms_accepted', 'provider_terms',
            'comment', 'created_at'
        ]
        read_only_fields = ['rental_price', 'delivery_price', 'deposit', 'total_price', 'status', 'total_days']
    
    def get_provider_terms(self, obj):
        """Получить правила прокатчика для данной брони"""
        if obj.car and obj.car.rental_provider:
            return obj.car.rental_provider.terms
        return None


class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'car', 'telegram_id', 'start_date', 'end_date', 
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
        
        car = data['car']
        conflicting_bookings = Booking.objects.filter(
            car=car,
            status__in=['confirmed', 'active', 'pending'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("На выбранные даты автомобиль уже забронирован")
        
        return data
    
    def create(self, validated_data):
        booking = Booking.objects.create(**validated_data)
        return booking
    

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'icon']

class CarListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка автомобилей (карточек)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_icon = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    first_image = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)
    price_for_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'brand', 'brand_name', 'brand_icon', 'category_title', 
            'year', 'color', 'engine_volume', 'mileage', 'transmission', 'oil_type',
            'price_per_day', 'deposit', 'status', 'features', 'first_image', 'city',
            'price_for_days'
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
    
    def get_price_for_days(self, obj):
        """Возвращает расчет цен для разных периодов"""
        return {
            '1_day': obj.get_price_for_days(1),
            '3_days': obj.get_price_for_days(3),
            '7_days': obj.get_price_for_days(7),
            '30_days': obj.get_price_for_days(30),
        }
    

class CarModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'brand_name', 'name', 'icon']
