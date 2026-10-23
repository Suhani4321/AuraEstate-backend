from django.contrib import admin
from django.utils.html import format_html
from .models import Agent, Property, PropertyImage, PropertyInquiry


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('avatar_preview', 'name', 'title', 'email', 'phone', 'properties_count', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'email', 'phone', 'title')
    ordering = ('name',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 38px; height: 38px; border-radius: 50%; object-fit: cover;" />', obj.avatar)
        return format_html('<span style="display:inline-block; width: 38px; height: 38px; border-radius: 50%; background:#e2e8f0; text-align:center; line-height:38px; font-weight:bold; color:#64748b;">{}</span>', obj.name[:1] if obj.name else '?')
    avatar_preview.short_description = 'Avatar'

    def properties_count(self, obj):
        return obj.properties.count()
    properties_count.short_description = 'Listings'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price', 'agent', 'property_type', 'listing_status', 'bedrooms', 'bathrooms', 'created_at')
    list_filter = ('agent', 'listing_status', 'property_type', 'city', 'is_featured')
    search_fields = ('title', 'address', 'city', 'zip_code', 'description', 'agent__name')
    raw_id_fields = ('agent',)
    inlines = [PropertyImageInline]


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'inquiry_type', 'created_at')
    list_filter = ('inquiry_type', 'created_at')
    search_fields = ('name', 'email', 'property__title')
