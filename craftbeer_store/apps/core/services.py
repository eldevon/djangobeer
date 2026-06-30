from typing import Optional, List, Dict, Any
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import BeerProduct, Order, OrderItem, ContactMessage
from decimal import Decimal
import uuid

# Dependency Inversion Principle: The High-level modules depend on abstractions
# Interface Segregation Principle: Services have specific, focused interfaces

class ProductService:
    """Service for product-related operations"""
    
    @staticmethod
    def get_products_by_category(category_slug: str) -> List[BeerProduct]:
        """Get products by category slug"""
        return BeerProduct.objects.filter(
            category__slug=category_slug,
            is_available=True,
            is_active=True
        )
    
    @staticmethod
    def get_featured_products(limit: int = 6) -> List[BeerProduct]:
        """Get featured products"""
        return BeerProduct.objects.filter(
            is_featured=True,
            is_available=True,
            is_active=True
        )[:limit]
    
    @staticmethod
    def search_products(query: str) -> List[BeerProduct]:
        """Search products by name or description"""
        return BeerProduct.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query) |
            models.Q(style__icontains=query),
            is_available=True,
            is_active=True
        )
    
    @staticmethod
    def update_stock(product_id: int, quantity: int) -> bool:
        """Update product stock quantity"""
        try:
            product = BeerProduct.objects.get(id=product_id)
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.is_available = product.stock_quantity > 0
                product.save()
                return True
            return False
        except BeerProduct.DoesNotExist:
            return False

class OrderService:
    """Service for order-related operations"""
    
    @staticmethod
    def create_order(user: User, items: List[Dict[str, Any]], 
                    shipping_address: str, notes: str = '') -> Order:
        """Create a new order"""
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        total = Decimal('0.00')
        for item in items:
            product = BeerProduct.objects.get(id=item['product_id'])
            total += product.price * Decimal(str(item['quantity']))
        
        # Create order
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_amount=total,
            shipping_address=shipping_address,
            notes=notes
        )
        
        # Create order items
        for item in items:
            product = BeerProduct.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=product.price
            )
            # Update stock
            ProductService.update_stock(product.id, item['quantity'])
        
        return order
    
    @staticmethod
    def get_user_orders(user: User) -> List[Order]:
        """Get all orders for a user"""
        return Order.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def update_order_status(order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
            return order
        except Order.DoesNotExist:
            return None

class ContactService:
    """Service for contact message operations"""
    
    @staticmethod
    def create_message(name: str, email: str, subject: str, message: str) -> ContactMessage:
        """Create a new contact message"""
        return ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
    
    @staticmethod
    def mark_as_read(message_id: int) -> Optional[ContactMessage]:
        """Mark a message as read"""
        try:
            message = ContactMessage.objects.get(id=message_id)
            message.is_read = True
            message.save()
            return message
        except ContactMessage.DoesNotExist:
            return None

class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user_profile(user: User, phone: str = '', address: str = '') -> None:
        """Create user profile"""
        from .models import UserProfile
        UserProfile.objects.create(user=user, phone=phone, address=address)
    
    @staticmethod
    def toggle_favorite_beer(user: User, product_id: int) -> bool:
        """Toggle favorite status for a beer"""
        try:
            product = BeerProduct.objects.get(id=product_id)
            profile = user.profile
            if product in profile.favorite_beers.all():
                profile.favorite_beers.remove(product)
                return False  # Removed from favorites
            else:
                profile.favorite_beers.add(product)
                return True  # Added to favorites
        except (BeerProduct.DoesNotExist, UserProfile.DoesNotExist):
            return False