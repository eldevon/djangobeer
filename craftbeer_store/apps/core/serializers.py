from rest_framework import serializers
from django.contrib.auth.models import User
from .models import BeerProduct, Category, Order, OrderItem, ContactMessage, UserProfile

# Single Responsibility Principle: Each serializer handles only one model
# Open/Closed Principle: Serializers can be extended

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']

class BeerProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = BeerProduct
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'abv', 'ibu', 'style', 'category', 'category_name',
            'stock_quantity', 'image', 'is_featured', 'is_available',
            'created_at', 'updated_at'
        ]

class BeerProductListSerializer(serializers.ModelSerializer):
    """Minimal serializer for list views"""
    class Meta:
        model = BeerProduct
        fields = ['id', 'name', 'slug', 'price', 'style', 'abv', 'image', 'is_available']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone', 'address', 'favorite_beers']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'total_amount', 'status',
            'shipping_address', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'created_at', 'updated_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at']
        read_only_fields = ['is_read', 'created_at']