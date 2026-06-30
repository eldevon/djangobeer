from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    ProductViewSet, CategoryViewSet, OrderViewSet,
    ContactViewSet, RegisterView, UserProfileView,
    toggle_favorite
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'contact', ContactViewSet, basename='contact')

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User registration
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # User profile
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Toggle favorite
    path('user/favorite/<int:product_id>/', toggle_favorite, name='toggle_favorite'),
    
    # Include router URLs
    path('', include(router.urls)),
]