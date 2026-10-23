from django.db.models import Q, Min, Max, Count, Avg
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Agent, Property, PropertyImage, PropertyInquiry
from .serializers import (
    AgentSerializer,
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyInquirySerializer,
)
from .email_service import send_inquiry_notification


class PropertyPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 50


class PropertyListView(generics.ListAPIView):
    """
    Search and Filter API for real estate properties.
    Supports filtering by search query, status, type, city, price range, bedrooms,
    bathrooms, area, amenities, and sorting.
    """
    serializer_class = PropertyListSerializer
    pagination_class = PropertyPagination

    def get_queryset(self):
        queryset = Property.objects.all().prefetch_related('gallery_images')
        params = self.request.query_params

        # 1. Search Query
        q = params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(address__icontains=q) |
                Q(city__icontains=q) |
                Q(state__icontains=q) |
                Q(zip_code__icontains=q)
            )

        # 2. Listing Status (for_sale, for_rent)
        listing_status = params.get('listing_status')
        if listing_status:
            queryset = queryset.filter(listing_status=listing_status)

        # 3. Property Type
        property_types = params.get('property_type')
        if property_types:
            types_list = [t.strip() for t in property_types.split(',') if t.strip()]
            if types_list:
                queryset = queryset.filter(property_type__in=types_list)

        # 4. City / Location
        city = params.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)

        # 5. Price Range
        min_price = params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # 6. Bedrooms
        bedrooms = params.get('bedrooms')
        if bedrooms:
            try:
                queryset = queryset.filter(bedrooms__gte=int(bedrooms))
            except ValueError:
                pass

        # 7. Bathrooms
        bathrooms = params.get('bathrooms')
        if bathrooms:
            try:
                queryset = queryset.filter(bathrooms__gte=float(bathrooms))
            except ValueError:
                pass

        # 8. Area (sqft)
        min_area = params.get('min_area')
        if min_area:
            try:
                queryset = queryset.filter(area_sqft__gte=int(min_area))
            except ValueError:
                pass

        max_area = params.get('max_area')
        if max_area:
            try:
                queryset = queryset.filter(area_sqft__lte=int(max_area))
            except ValueError:
                pass

        # 9. Amenities Filter (filter properties containing specified amenities)
        amenities_param = params.get('amenities')
        if amenities_param:
            selected_amenities = [a.strip() for a in amenities_param.split(',') if a.strip()]
            for amenity in selected_amenities:
                queryset = queryset.filter(amenities__icontains=amenity)

        # 10. Featured filter
        featured = params.get('featured')
        if featured in ['true', '1']:
            queryset = queryset.filter(is_featured=True)

        # 11. Sorting
        sort_by = params.get('sort', 'newest')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'area_desc':
            queryset = queryset.order_by('-area_sqft')
        elif sort_by == 'bedrooms_desc':
            queryset = queryset.order_by('-bedrooms')
        else: # default newest
            queryset = queryset.order_by('-created_at')

        return queryset


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all().prefetch_related('gallery_images')
    serializer_class = PropertyDetailSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Property.objects.filter(id=instance.id).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedPropertiesView(generics.ListAPIView):
    serializer_class = PropertyListSerializer
    pagination_class = None

    def get_queryset(self):
        return Property.objects.filter(is_featured=True)[:6]


class PropertyMetadataView(views.APIView):
    """
    Returns available categories, cities, price bounds, and stats for dynamic filters.
    """
    def get(self, request):
        total_properties = Property.objects.count()
        price_stats = Property.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            min_area=Min('area_sqft'),
            max_area=Max('area_sqft')
        )

        cities = (
            Property.objects.values('city')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        property_types = (
            Property.objects.values('property_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        all_amenities = [
            'Swimming Pool', 'Central AC', 'Private Balcony', 'Garage Parking',
            'Fitness Center', 'Pet Friendly', 'Ocean View', 'Garden / Patio',
            'Smart Home System', '24/7 Security', 'Walk-in Closet', 'Hardwood Floors'
        ]

        return Response({
            'total_properties': total_properties,
            'price_stats': {
                'min_price': float(price_stats['min_price'] or 0),
                'max_price': float(price_stats['max_price'] or 0),
                'avg_price': round(float(price_stats['avg_price'] or 0), 2),
                'min_area': price_stats['min_area'] or 0,
                'max_area': price_stats['max_area'] or 0,
            },
            'cities': list(cities),
            'property_types': list(property_types),
            'amenities': all_amenities
        })


class PropertyInquiryCreateView(generics.CreateAPIView):
    queryset = PropertyInquiry.objects.all()
    serializer_class = PropertyInquirySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()

        # Send email to listing agent and confirmation to client
        email_sent = send_inquiry_notification(inquiry)

        agent = getattr(inquiry.property, 'agent', None)
        agent_name = agent.name if agent else inquiry.property.agent_name
        agent_email = agent.email if agent else inquiry.property.agent_email

        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data.copy()
        response_data['email_sent'] = email_sent
        response_data['agent_name'] = agent_name
        response_data['agent_email'] = agent_email

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class AgentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all listing agents or create a new agent.
    """
    queryset = Agent.objects.all().prefetch_related('properties')
    serializer_class = AgentSerializer


class AgentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a listing agent.
    """
    queryset = Agent.objects.all().prefetch_related('properties')
    serializer_class = AgentSerializer
    lookup_field = 'id'
