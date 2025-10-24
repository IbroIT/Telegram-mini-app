from rest_framework import serializers
from .models import Car, Booking, Category, Feature, CarImage


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
    user_name = serializers.CharField(source='user.username', read_only=True)
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'car', 'car_title', 'user', 'user_name',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'status', 'total_days']


class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['car', 'start_date', 'end_date']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Пользователь должен быть авторизован")
        
        car = validated_data['car']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        days = (end_date - start_date).days
        if days <= 0:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
        total_price = days * car.price_per_day
        
        booking = Booking.objects.create(
            car=car,
            user=user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='pending'
        )
        return booking
