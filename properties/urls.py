from django.urls import path
from .views import (
    PropertyListView,
    PropertyDetailView,
    FeaturedPropertiesView,
    PropertyMetadataView,
    PropertyInquiryCreateView,
    AgentListCreateView,
    AgentDetailView,
)

urlpatterns = [
    path('properties/', PropertyListView.as_view(), name='property-list'),
    path('properties/<int:id>/', PropertyDetailView.as_view(), name='property-detail'),
    path('properties/featured/', FeaturedPropertiesView.as_view(), name='property-featured'),
    path('properties/meta/', PropertyMetadataView.as_view(), name='property-metadata'),
    path('properties/inquiry/', PropertyInquiryCreateView.as_view(), name='property-inquiry'),
    path('agents/', AgentListCreateView.as_view(), name='agent-list-create'),
    path('agents/<int:id>/', AgentDetailView.as_view(), name='agent-detail'),
]
