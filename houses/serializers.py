from rest_framework import serializers
from .models import HouseCategory, HouseFeature, House, HouseImage, HouseBooking, HousePriceTier
from core.serializers import CitySerializer, DeliveryZoneSerializer, RentalProviderSerializer

class HouseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseCategory
        fields = ['id', 'title', 'icon']

class HouseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseFeature
        fields = ['id', 'title']

class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = ['id', 'image', 'order']


class HousePriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousePriceTier
        fields = ['id', 'min_days', 'price_per_day', 'is_active']


class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = HouseFeatureSerializer(many=True, read_only=True)
    city = CitySerializer(read_only=True)
    rental_provider = RentalProviderSerializer(read_only=True)
    delivery_zones = DeliveryZoneSerializer(many=True, read_only=True)
    price_tiers = HousePriceTierSerializer(many=True, read_only=True)
    
    class Meta:
        model = House
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'floors', 'area', 'price_per_day', 'deposit', 'status', 
            'features', 'images', 'city', 'rental_provider', 'delivery_zones',
            'price_tiers', 'created_at'
        ]


class HouseBookingSerializer(serializers.ModelSerializer):
    house_title = serializers.CharField(source='house.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    city = CitySerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    provider_terms = serializers.SerializerMethodField()
    
    class Meta:
        model = HouseBooking
        fields = [
            'id', 'house', 'house_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'city', 'delivery_zone', 
            'rental_price', 'delivery_price', 'deposit', 'total_price',
            'provider_terms_accepted', 'service_terms_accepted', 'provider_terms',
            'comment', 'created_at'
        ]
        read_only_fields = ['rental_price', 'delivery_price', 'deposit', 'total_price', 'status', 'total_days']
    
    def get_provider_terms(self, obj):
        """Получить правила прокатчика для данной брони"""
        if obj.house and obj.house.rental_provider:
            return obj.house.rental_provider.terms
        return None


class CreateHouseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseBooking
        fields = [
            'house', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'city', 'delivery_zone',
            'provider_terms_accepted', 'service_terms_accepted', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")
        
        # Проверка согласия с правилами
        if not data.get('provider_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами прокатчика")
        
        if not data.get('service_terms_accepted', False):
            raise serializers.ValidationError("Необходимо согласиться с правилами сервиса")
        
        house = data['house']
        conflicting_bookings = HouseBooking.objects.filter(
            house=house,
            status__in=['confirmed', 'active', 'pending'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("На выбранные даты дом уже забронирован")
        
        return data
    
    def create(self, validated_data):
        booking = HouseBooking.objects.create(**validated_data)
        return booking
    
class HouseListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка домов (карточек)"""
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = HouseFeatureSerializer(many=True, read_only=True)
    first_image = serializers.SerializerMethodField()
    price_per_day = serializers.IntegerField()
    
    class Meta:
        model = House
        fields = [
            'id', 'title', 'category_title', 'floors', 'area',
            'price_per_day', 'deposit', 'status', 'features', 'first_image'
        ]
    
    def get_first_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None