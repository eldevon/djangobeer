from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import BeerProduct, Category
from .services import ProductService, ContactService
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def home_view(request):
    """Home page view"""
    featured_products = ProductService.get_featured_products(limit=6)
    categories = Category.objects.filter(is_active=True)[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'title': 'Craft Beer Store - Home'
    }
    return render(request, 'home.html', context)

def about_view(request):
    """About page view"""
    context = {
        'title': 'About Us - Craft Beer Store'
    }
    return render(request, 'about.html', context)

def products_view(request):
    """Products page view"""
    products = BeerProduct.objects.filter(is_available=True, is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    style = request.GET.get('style')
    search_query = request.GET.get('search')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if style:
        products = products.filter(style__iexact=style)
    
    if search_query:
        products = ProductService.search_products(search_query)
    
    # Get all available styles for filter
    styles = BeerProduct.objects.filter(is_available=True).values_list('style', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'styles': styles,
        'current_category': category_slug,
        'current_style': style,
        'title': 'Products - Craft Beer Store'
    }
    return render(request, 'products.html', context)

def product_detail_view(request, slug):
    """Product detail page"""
    product = get_object_or_404(BeerProduct, slug=slug, is_available=True)
    related_products = BeerProduct.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'title': f'{product.name} - Craft Beer Store'
    }
    return render(request, 'product_detail.html', context)

def contact_view(request):
    """Contact page view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save to database using service
        ContactService.create_message(name, email, subject, message)
        
        # Send email notification
        try:
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail
            pass
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return render(request, 'contact.html', {'title': 'Contact - Craft Beer Store'})
    
    context = {
        'title': 'Contact - Craft Beer Store'
    }
    return render(request, 'contact.html', context)