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
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = HouseBooking
        fields = [
            'id', 'house', 'house_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'total_days']

class CreateHouseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseBooking
        fields = [
            'house', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'comment'
        ]
    
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
        house = validated_data['house']
        telegram_id = validated_data['telegram_id']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        client_name = validated_data['client_name']
        phone_number = validated_data['phone_number']
        comment = validated_data.get('comment', '')
        
        total_days = (end_date - start_date).days + 1
        total_price = total_days * house.price_per_day
        
        booking = HouseBooking.objects.create(
            house=house,
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