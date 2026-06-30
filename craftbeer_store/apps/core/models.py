from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

# Single Responsibility Principle: Each model handles only one specific entity
# Open/Closed Principle: Models can be extended without modification

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class BeerProduct(BaseModel):
    """Beer product model following Single Responsibility Principle"""
    # Product information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Beer specific attributes
    abv = models.DecimalField(max_digits=4, decimal_places=1, 
                             validators=[MinValueValidator(0), MaxValueValidator(20)])
    ibu = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    style = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Inventory and media
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Availability flags
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_available']),
        ]

class Order(BaseModel):
    """Order model following Single Responsibility Principle"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    shipping_address = models.TextField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(BaseModel):
    """Order item model following Single Responsibility Principle"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(BeerProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_subtotal(self):
        return self.quantity * self.price

class ContactMessage(BaseModel):
    """Contact message model"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}"

    class Meta:
        ordering = ['-created_at']

class UserProfile(BaseModel):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    favorite_beers = models.ManyToManyField(BeerProduct, blank=True, related_name='favorited_by')

    def __str__(self):
        return f"Profile of {self.user.username}"
