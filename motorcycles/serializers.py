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
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = MotoBooking
        fields = [
            'id', 'motorcycle', 'motorcycle_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'total_days']

class CreateMotoBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotoBooking
        fields = [
            'motorcycle', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
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
        motorcycle = validated_data['motorcycle']
        telegram_id = validated_data['telegram_id']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        client_name = validated_data['client_name']
        phone_number = validated_data['phone_number']
        comment = validated_data.get('comment', '')
        
        total_days = (end_date - start_date).days + 1
        total_price = total_days * motorcycle.price_per_day
        
        booking = MotoBooking.objects.create(
            motorcycle=motorcycle,
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