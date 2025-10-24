from rest_framework import serializers
from .models import MotoCategory, MotoFeature, Motorcycle, MotoImage, MotoBooking

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

class MotorcycleSerializer(serializers.ModelSerializer):
    images = MotoImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = MotoFeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Motorcycle
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'year', 'color', 'engine_volume', 'mileage', 'transmission',
            'oil_type', 'bike_type', 'power', 'price_per_day', 'deposit', 
            'status', 'features', 'images', 'created_at'
        ]

class MotoBookingSerializer(serializers.ModelSerializer):
    motorcycle_title = serializers.CharField(source='motorcycle.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MotoBooking
        fields = [
            'id', 'motorcycle', 'motorcycle_title', 'user', 'user_name',
            'start_date', 'end_date', 'status', 'total_price',
            'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'status']

class CreateMotoBookingSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования мотоцикла без указания пользователя"""
    class Meta:
        model = MotoBooking
        fields = ['motorcycle', 'start_date', 'end_date']
    
    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Пользователь должен быть авторизован")
        
        motorcycle = validated_data['motorcycle']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        days = (end_date - start_date).days
        if days <= 0:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
        total_price = days * motorcycle.price_per_day
        
        booking = MotoBooking.objects.create(
            motorcycle=motorcycle,
            user=user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='pending'
        )
        
        return booking