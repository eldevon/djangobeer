from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import register_view
from core.views import (
    home_view, about_view, products_view, 
    contact_view, product_detail_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Frontend URLs
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('products/', products_view, name='products'),
    path('products/<slug:slug>/', product_detail_view, name='product_detail'),
    path('contact/', contact_view, name='contact'),
    
    # API URLs
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)