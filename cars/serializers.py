from rest_framework import serializers
from .models import Car, Booking, Category, Feature, CarImage, Brand


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

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'year', 'color', 'engine_volume', 'mileage', 'transmission',
            'oil_type', 'price_per_day', 'deposit', 'status',
            'features', 'images', 'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    car_title = serializers.CharField(source='car.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'car', 'car_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'total_days']

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'car', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
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
        car = validated_data['car']
        telegram_id = validated_data['telegram_id']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        client_name = validated_data['client_name']
        phone_number = validated_data['phone_number']
        comment = validated_data.get('comment', '')
        
        total_days = (end_date - start_date).days + 1
        total_price = total_days * car.price_per_day
        
        booking = Booking.objects.create(
            car=car,
            telegram_id=telegram_id,
            start_date=start_date,
            end_date=end_date,
            client_name=client_name,
            phone_number=phone_number,
            comment=comment,
            total_price=total_price,
            status='pending'
        )
        
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
    price_per_day = serializers.IntegerField()
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'brand', 'brand_name', 'brand_icon', 'category_title', 
            'year', 'color', 'engine_volume', 'mileage', 'transmission', 'oil_type',
            'price_per_day', 'deposit', 'status', 'features', 'first_image'
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