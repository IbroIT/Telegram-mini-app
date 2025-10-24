from rest_framework import serializers
from .models import HouseCategory, HouseFeature, House, HouseImage, HouseBooking

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

class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = HouseFeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = House
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'floors', 'area', 'price_per_day', 'deposit', 'status', 
            'features', 'images', 'created_at'
        ]
class HouseBookingSerializer(serializers.ModelSerializer):
    house_title = serializers.CharField(source='house.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = HouseBooking
        fields = [
            'id', 'house', 'house_title', 'user', 'user_name',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'status', 'total_days']

class CreateHouseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseBooking
        fields = ['house', 'start_date', 'end_date', 'client_name', 'phone_number', 'comment']
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")
        
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
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Пользователь должен быть авторизован")
        
        house = validated_data['house']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        client_name = validated_data['client_name']
        phone_number = validated_data['phone_number']
        comment = validated_data.get('comment', '')
        
        total_days = (end_date - start_date).days + 1
        total_price = total_days * house.price_per_day
        
        booking = HouseBooking.objects.create(
            house=house,
            user=user,
            start_date=start_date,
            end_date=end_date,
            client_name=client_name,
            phone_number=phone_number,
            comment=comment,
            total_price=total_price,
            status='pending'
        )
        
        return booking
    """Сериализатор для создания бронирования дома без указания пользователя"""
    class Meta:
        model = HouseBooking
        fields = ['house', 'start_date', 'end_date', 'guests']
    
    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Пользователь должен быть авторизован")
        
        house = validated_data['house']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        guests = validated_data.get('guests', 1)
        
        days = (end_date - start_date).days
        if days <= 0:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")
        
        total_price = days * house.price_per_day
        
        booking = HouseBooking.objects.create(
            house=house,
            user=user,
            start_date=start_date,
            end_date=end_date,
            guests=guests,
            total_price=total_price,
            status='pending'
        )
        
        return booking