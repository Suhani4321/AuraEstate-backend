from django.db import models
from django.utils.text import slugify
import uuid


class Agent(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, default='Luxury Portfolio Specialist', blank=True)
    phone = models.CharField(max_length=40)
    email = models.EmailField(unique=True)
    avatar = models.URLField(max_length=600, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Listing Agent'
        verbose_name_plural = 'Listing Agents'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'Single Family House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('penthouse', 'Luxury Penthouse'),
        ('villa', 'Modern Villa'),
        ('commercial', 'Commercial Space'),
    ]

    LISTING_STATUSES = [
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
        ('pending', 'Pending Sale'),
        ('sold', 'Sold'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES, db_index=True)
    listing_status = models.CharField(max_length=20, choices=LISTING_STATUSES, default='for_sale', db_index=True)
    
    price = models.DecimalField(max_digits=14, decimal_places=2, db_index=True)
    bedrooms = models.PositiveSmallIntegerField(default=1, db_index=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, db_index=True)
    area_sqft = models.PositiveIntegerField(db_index=True)
    lot_size_sqft = models.PositiveIntegerField(null=True, blank=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    garage_spaces = models.PositiveSmallIntegerField(default=1)
    
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, db_index=True)
    zip_code = models.CharField(max_length=20, db_index=True)
    country = models.CharField(max_length=60, default='India')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    featured_image = models.URLField(max_length=600)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=True)
    hoa_fee_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Store list of strings, e.g. ["Swimming Pool", "Central AC", "Ocean View"]
    amenities = models.JSONField(default=list, blank=True)
    
    # Agent info
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    agent_name = models.CharField(max_length=120, default='Sarah Jenkins', blank=True)
    agent_phone = models.CharField(max_length=40, default='+1 (555) 382-9901', blank=True)
    agent_email = models.EmailField(default='sarah.jenkins@luxurydwell.com', blank=True)
    agent_avatar = models.URLField(max_length=600, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['price', 'property_type']),
            models.Index(fields=['city', 'listing_status']),
            models.Index(fields=['bedrooms', 'bathrooms']),
        ]

    def save(self, *args, **kwargs):
        if self.agent:
            self.agent_name = self.agent.name
            self.agent_phone = self.agent.phone
            self.agent_email = self.agent.email
            self.agent_avatar = self.agent.avatar
        if not self.slug:
            base_slug = slugify(self.title)
            unique_id = uuid.uuid4().hex[:6]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)

    @property
    def google_maps_url(self):
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        import urllib.parse
        parts = [self.address, self.city, self.state, self.zip_code, self.country]
        query = ", ".join([str(p) for p in parts if p])
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"

    def __str__(self):
        return f"{self.title} - ₹{self.price:,.0f} ({self.city})"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='gallery_images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=600)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.property.title} (#{self.order})"




class PropertyInquiry(models.Model):
    property = models.ForeignKey(Property, related_name='inquiries', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=40, default='Schedule a Tour')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.name} for {self.property.title}"
