from rest_framework import serializers
from .models import Agent, Property, PropertyImage, PropertyInquiry


class AgentSerializer(serializers.ModelSerializer):
    properties_count = serializers.IntegerField(source='properties.count', read_only=True)

    class Meta:
        model = Agent
        fields = ['id', 'name', 'title', 'phone', 'email', 'avatar', 'bio', 'properties_count']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'caption', 'order']


def format_inr(amount, is_rent=False):
    amt = float(amount)
    if is_rent:
        if amt >= 100000:
            val = amt / 100000
            formatted = f"{val:.2f}".rstrip('0').rstrip('.')
            return f"₹{formatted} L/mo"
        return f"₹{amt:,.0f}/mo"
    else:
        if amt >= 10000000:
            val = amt / 10000000
            formatted = f"{val:.2f}".rstrip('0').rstrip('.')
            return f"₹{formatted} Cr"
        elif amt >= 100000:
            val = amt / 100000
            formatted = f"{val:.2f}".rstrip('0').rstrip('.')
            return f"₹{formatted} Lakh"
        return f"₹{amt:,.0f}"


class PropertyListSerializer(serializers.ModelSerializer):
    price_formatted = serializers.SerializerMethodField()
    price_per_sqft = serializers.SerializerMethodField()
    google_maps_url = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'slug',
            'property_type',
            'listing_status',
            'price',
            'price_formatted',
            'price_per_sqft',
            'bedrooms',
            'bathrooms',
            'area_sqft',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'latitude',
            'longitude',
            'google_maps_url',
            'featured_image',
            'is_featured',
            'is_verified',
            'year_built',
            'garage_spaces',
            'amenities',
            'created_at',
        ]

    def get_price_formatted(self, obj):
        return format_inr(obj.price, is_rent=(obj.listing_status == 'for_rent'))

    def get_price_per_sqft(self, obj):
        if obj.area_sqft and obj.area_sqft > 0:
            return round(float(obj.price) / obj.area_sqft, 1)
        return 0


class PropertyDetailSerializer(serializers.ModelSerializer):
    gallery_images = PropertyImageSerializer(many=True, read_only=True)
    price_formatted = serializers.SerializerMethodField()
    price_per_sqft = serializers.SerializerMethodField()
    google_maps_url = serializers.ReadOnlyField()
    agent = AgentSerializer(read_only=True)
    agent_name = serializers.SerializerMethodField()
    agent_phone = serializers.SerializerMethodField()
    agent_email = serializers.SerializerMethodField()
    agent_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'property_type',
            'listing_status',
            'price',
            'price_formatted',
            'price_per_sqft',
            'bedrooms',
            'bathrooms',
            'area_sqft',
            'lot_size_sqft',
            'year_built',
            'garage_spaces',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'latitude',
            'longitude',
            'google_maps_url',
            'featured_image',
            'is_featured',
            'is_verified',
            'hoa_fee_monthly',
            'views_count',
            'amenities',
            'agent',
            'agent_name',
            'agent_phone',
            'agent_email',
            'agent_avatar',
            'gallery_images',
            'created_at',
            'updated_at',
        ]

    def get_agent_name(self, obj):
        return obj.agent.name if obj.agent else obj.agent_name

    def get_agent_phone(self, obj):
        return obj.agent.phone if obj.agent else obj.agent_phone

    def get_agent_email(self, obj):
        return obj.agent.email if obj.agent else obj.agent_email

    def get_agent_avatar(self, obj):
        return obj.agent.avatar if obj.agent else obj.agent_avatar

    def get_price_formatted(self, obj):
        return format_inr(obj.price, is_rent=(obj.listing_status == 'for_rent'))

    def get_price_per_sqft(self, obj):
        if obj.area_sqft and obj.area_sqft > 0:
            return round(float(obj.price) / obj.area_sqft, 1)
        return 0




class PropertyInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInquiry
        fields = '__all__'
