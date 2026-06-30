from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, BeerProduct
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with initial craft beer data'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = [
            {'name': 'IPA', 'slug': 'ipa', 'description': 'India Pale Ales - hoppy and bold'},
            {'name': 'Stout', 'slug': 'stout', 'description': 'Dark, rich, and creamy stouts'},
            {'name': 'Pale Ale', 'slug': 'pale-ale', 'description': 'Classic pale ales with balanced flavors'},
            {'name': 'Wheat Beer', 'slug': 'wheat-beer', 'description': 'Refreshing wheat-based beers'},
            {'name': 'Sour', 'slug': 'sour', 'description': 'Tart and funky sour ales'},
            {'name': 'Lager', 'slug': 'lager', 'description': 'Crisp and clean lagers'},
        ]

        category_objects = {}
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            category_objects[cat_data['slug']] = cat
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        # Create 6 beer products
        beers = [
            {
                'name': 'Hazy IPA',
                'slug': 'hazy-ipa',
                'description': 'A juicy, hazy IPA bursting with tropical fruit flavors and a smooth, creamy mouthfeel. Perfect for IPA lovers seeking something different.',
                'price': Decimal('12.99'),
                'abv': Decimal('6.5'),
                'ibu': 45,
                'style': 'IPA',
                'category': category_objects['ipa'],
                'stock_quantity': 50,
                'is_featured': True,
                'is_available': True,
            },
            {
                'name': 'Imperial Stout',
                'slug': 'imperial-stout',
                'description': 'A bold, robust stout with notes of dark chocolate, coffee, and dried fruit. Rich and warming with a velvety smooth finish.',
                'price': Decimal('14.99'),
                'abv': Decimal('9.0'),
                'ibu': 65,
                'style': 'Stout',
                'category': category_objects['stout'],
                'stock_quantity': 30,
                'is_featured': True,
                'is_available': True,
            },
            {
                'name': 'West Coast Pale Ale',
                'slug': 'west-coast-pale-ale',
                'description': 'A crisp, refreshing pale ale with pronounced citrus and pine notes from generous hop additions. Clean finish with a balanced malt backbone.',
                'price': Decimal('10.99'),
                'abv': Decimal('5.5'),
                'ibu': 35,
                'style': 'Pale Ale',
                'category': category_objects['pale-ale'],
                'stock_quantity': 60,
                'is_featured': False,
                'is_available': True,
            },
            {
                'name': 'Belgian Witbier',
                'slug': 'belgian-witbier',
                'description': 'A traditional Belgian wheat beer with subtle spice notes of coriander and orange peel. Cloudy and refreshing with a light, crisp finish.',
                'price': Decimal('11.99'),
                'abv': Decimal('4.8'),
                'ibu': 15,
                'style': 'Wheat Beer',
                'category': category_objects['wheat-beer'],
                'stock_quantity': 45,
                'is_featured': False,
                'is_available': True,
            },
            {
                'name': 'Berry Sour',
                'slug': 'berry-sour',
                'description': 'A tart and refreshing sour ale loaded with mixed berries. Complex flavors with a perfect balance of sweet and sour notes.',
                'price': Decimal('13.99'),
                'abv': Decimal('4.5'),
                'ibu': 8,
                'style': 'Sour',
                'category': category_objects['sour'],
                'stock_quantity': 35,
                'is_featured': True,
                'is_available': True,
            },
            {
                'name': 'Pilsner',
                'slug': 'pilsner',
                'description': 'A classic German-style pilsner with a crisp, clean taste and subtle hop bitterness. Exceptionally drinkable with a noble hop character.',
                'price': Decimal('9.99'),
                'abv': Decimal('4.5'),
                'ibu': 30,
                'style': 'Lager',
                'category': category_objects['lager'],
                'stock_quantity': 70,
                'is_featured': False,
                'is_available': True,
            },
        ]

        for beer_data in beers:
            beer, created = BeerProduct.objects.get_or_create(
                slug=beer_data['slug'],
                defaults=beer_data
            )
            if created:
                self.stdout.write(f'Created beer: {beer.name}')
            else:
                # Update existing beer
                for key, value in beer_data.items():
                    setattr(beer, key, value)
                beer.save()
                self.stdout.write(f'Updated beer: {beer.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with craft beer data!'))