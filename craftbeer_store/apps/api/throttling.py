from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache

class ContactRateThrottle(AnonRateThrottle):
    """Rate limiting specifically for contact form submissions"""
    rate = '5/hour'  # 5 submissions per hour for anonymous users

class ProductRateThrottle(AnonRateThrottle):
    """Rate limiting for product API endpoints"""
    rate = '200/day'
    
class OrderRateThrottle(UserRateThrottle):
    """Rate limiting for order endpoints"""
    rate = '50/day'