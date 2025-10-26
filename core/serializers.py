from rest_framework import serializers
from .models import City, DeliveryZone, RentalProvider, ServiceTerms


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'is_active', 'order']


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'price', 'is_active', 'order']


class RentalProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalProvider
        fields = ['id', 'name', 'contact_person', 'phone', 'email', 'telegram', 
                 'terms', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ServiceTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTerms
        fields = ['id', 'title', 'content', 'is_active', 'updated_at']
        read_only_fields = ['updated_at']
