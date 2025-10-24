from rest_framework import serializers
from .models import ExcursionCategory, ExcursionFeature, Excursion, ExcursionImage, ExcursionBooking

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

class ExcursionSerializer(serializers.ModelSerializer):
    images = ExcursionImageSerializer(many=True, read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    features = ExcursionFeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'description', 'category', 'category_title',
            'days', 'price_per_person', 'status', 'features', 'images', 'created_at'
        ]

class ExcursionBookingSerializer(serializers.ModelSerializer):
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)
    total_days = serializers.ReadOnlyField()
    
    class Meta:
        model = ExcursionBooking
        fields = [
            'id', 'excursion', 'excursion_title', 'telegram_id',
            'start_date', 'end_date', 'total_days', 'client_name', 'phone_number',
            'status', 'total_price', 'comment', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'total_days']

class CreateExcursionBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionBooking
        fields = [
            'excursion', 'telegram_id', 'start_date', 'end_date', 
            'client_name', 'phone_number', 'comment'
        ]
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")
        
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
        excursion = validated_data['excursion']
        telegram_id = validated_data['telegram_id']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        client_name = validated_data['client_name']
        phone_number = validated_data['phone_number']
        comment = validated_data.get('comment', '')
        
        total_days = (end_date - start_date).days + 1
        total_price = total_days * excursion.price_per_person
        
        booking = ExcursionBooking.objects.create(
            excursion=excursion,
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