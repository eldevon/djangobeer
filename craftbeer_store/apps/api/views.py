from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from core.models import BeerProduct, Category, Order, ContactMessage
from core.serializers import (
    BeerProductSerializer, BeerProductListSerializer, 
    CategorySerializer, OrderSerializer, ContactMessageSerializer,
    UserSerializer, UserProfileSerializer
)
from core.services import ProductService, OrderService, ContactService, UserService
from .throttling import ContactRateThrottle, ProductRateThrottle, OrderRateThrottle

# Single Responsibility Principle: Each view handles specific functionality

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products - read-only for public"""
    queryset = BeerProduct.objects.filter(is_available=True, is_active=True)
    serializer_class = BeerProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [ProductRateThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BeerProductListSerializer
        return BeerProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by style
        style = self.request.query_params.get('style')
        if style:
            queryset = queryset.filter(style__iexact=style)
        
        # Filter featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = ProductService.search_products(search)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = ProductService.get_featured_products(limit=6)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def styles(self, request):
        """Get all unique beer styles"""
        styles = BeerProduct.objects.values_list('style', flat=True).distinct()
        return Response({'styles': list(styles)})

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [ProductRateThrottle]

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for orders - user-specific"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderRateThrottle]
    
    def get_queryset(self):
        """Filter orders to only show user's own orders"""
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create order using service"""
        order_data = self.request.data
        items = order_data.get('items', [])
        shipping_address = order_data.get('shipping_address', '')
        notes = order_data.get('notes', '')
        
        # Use OrderService to create order
        order = OrderService.create_order(
            user=self.request.user,
            items=items,
            shipping_address=shipping_address,
            notes=notes
        )
        return order
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        if order.status not in ['PENDING', 'PROCESSING']:
            return Response(
                {'error': 'Order cannot be cancelled in its current state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'CANCELLED'
        order.save()
        return Response({'message': 'Order cancelled successfully'})

class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for contact messages"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [ContactRateThrottle]
    
    def perform_create(self, serializer):
        """Create contact message using service"""
        ContactService.create_message(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message']
        )

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(self.request.data.get('password'))
        user.save()
        # Create user profile
        UserService.create_user_profile(user)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, product_id):
    """Toggle favorite status for a beer"""
    result = UserService.toggle_favorite_beer(request.user, product_id)
    return Response({
        'is_favorite': result,
        'message': 'Favorite updated successfully' if result is not None else 'Product not found'
    })
