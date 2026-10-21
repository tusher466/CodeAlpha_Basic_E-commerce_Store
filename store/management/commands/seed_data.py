from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, ProductReview, Order, OrderItem


class Command(BaseCommand):
    help = 'Seeds initial sample data including categories, products, admin, and demo users.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Create Superuser and Demo User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@codealpha.tech',
                'first_name': 'CodeAlpha',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()

        # Also create admin user matching email as username for direct login
        admin_email_user, _ = User.objects.get_or_create(
            username='admin@codealpha.tech',
            defaults={
                'email': 'admin@codealpha.tech',
                'first_name': 'CodeAlpha',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_email_user.set_password('admin123')
        admin_email_user.is_staff = True
        admin_email_user.is_superuser = True
        admin_email_user.is_active = True
        admin_email_user.save()
        self.stdout.write(self.style.SUCCESS("Superusers ready: admin and admin@codealpha.tech (password: admin123 or admin)"))

        demo_user, u_created = User.objects.get_or_create(
            username='johndoe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
            }
        )
        if u_created:
            demo_user.set_password('password123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: johndoe / password123"))

        # 2. Categories
        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Smart devices, computing, and cutting-edge tech gadgets.',
                'icon': 'bi-laptop',
                'image_url': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=600&q=80',
            },
            {
                'name': 'Audio & Headphones',
                'slug': 'audio-headphones',
                'description': 'Premium noise-canceling headphones, wireless earbuds, and speakers.',
                'icon': 'bi-headphones',
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80',
            },
            {
                'name': 'Wearables & Smartwatches',
                'slug': 'wearables',
                'description': 'Fitness trackers, luxury smartwatches, and smart accessories.',
                'icon': 'bi-smartwatch',
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80',
            },
            {
                'name': 'Fashion & Lifestyle',
                'slug': 'fashion-lifestyle',
                'description': 'Trendy urban apparel, durable bags, and timeless accessories.',
                'icon': 'bi-bag-check',
                'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=600&q=80',
            },
            {
                'name': 'Home & Workspace',
                'slug': 'home-workspace',
                'description': 'Modern minimalist workspace setup, ergonomic chairs, and desk gear.',
                'icon': 'bi-lamp',
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=600&q=80',
            },
        ]

        cat_objs = {}
        for c in categories_data:
            obj, _ = Category.objects.update_or_create(
                slug=c['slug'],
                defaults=c
            )
            cat_objs[c['slug']] = obj

        # 3. Products
        products_data = [
            # Audio & Headphones
            {
                'category': cat_objs['audio-headphones'],
                'name': 'AlphaWave Pro Wireless Headphones',
                'slug': 'alphawave-pro-wireless-headphones',
                'brand': 'AlphaSound',
                'short_description': 'Active Noise Cancellation with 40-hour battery life and spatial audio.',
                'description': 'Experience studio-grade clarity with the AlphaWave Pro. Featuring custom 40mm beryllium drivers, active hybrid noise cancellation, plush memory foam ear cushions, and up to 40 hours of playtime on a single charge. Bluetooth 5.3 ensures seamless multi-point pairing.',
                'price': Decimal('189.99'),
                'original_price': Decimal('249.99'),
                'stock': 24,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'review_count': 38,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['audio-headphones'],
                'name': 'AlphaBeats True Wireless Earbuds',
                'slug': 'alphabeats-true-wireless-earbuds',
                'brand': 'AlphaSound',
                'short_description': 'Compact IPX7 waterproof earbuds with crisp bass and wireless charging.',
                'description': 'Designed for athletes and everyday commuters. Features touch controls, 32-hour total battery life with Qi wireless charging case, ultra-low latency gaming mode, and crystal clear call quality with 4 beamforming microphones.',
                'price': Decimal('79.99'),
                'original_price': Decimal('99.99'),
                'stock': 45,
                'is_featured': False,
                'rating': Decimal('4.6'),
                'review_count': 19,
                'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['audio-headphones'],
                'name': 'Pulse 360 Portable Bluetooth Speaker',
                'slug': 'pulse-360-portable-bluetooth-speaker',
                'brand': 'AlphaSound',
                'short_description': 'Deep 360-degree sound, rugged waterproof IP67 build, and RGB beat light.',
                'description': 'Take your soundtrack everywhere. Dual passive radiators deliver thunderous bass, while the integrated clip and shockproof silicone body withstand drops, pool splashes, and outdoor trails. 20 hours of continuous playback.',
                'price': Decimal('59.50'),
                'original_price': Decimal('79.00'),
                'stock': 30,
                'is_featured': False,
                'rating': Decimal('4.5'),
                'review_count': 14,
                'image_url': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80',
            },

            # Wearables
            {
                'category': cat_objs['wearables'],
                'name': 'Titan Apex GPS Smartwatch',
                'slug': 'titan-apex-gps-smartwatch',
                'brand': 'AlphaPulse',
                'short_description': 'AMOLED sapphire glass display, heart-rate tracking, ECG & multi-day battery.',
                'description': 'Built for extreme explorers and daily executives alike. Crafted with aerospace-grade titanium, always-on vibrant AMOLED display, SpO2 sensor, sleep staging, dual-band GPS, and 14-day battery life.',
                'price': Decimal('299.00'),
                'original_price': Decimal('349.00'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'review_count': 42,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['wearables'],
                'name': 'VibeFit Minimalist Fitness Band',
                'slug': 'vibefit-minimalist-fitness-band',
                'brand': 'AlphaPulse',
                'short_description': 'Lightweight featherweight fitness tracker with step, calorie and sleep monitor.',
                'description': 'Stay motivated with 24/7 activity monitoring, water resistance up to 50 meters, customizable sport modes, phone notifications, and an ultra-comfortable hypoallergenic silicone band.',
                'price': Decimal('49.99'),
                'original_price': Decimal('69.99'),
                'stock': 50,
                'is_featured': False,
                'rating': Decimal('4.4'),
                'review_count': 27,
                'image_url': 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=800&q=80',
            },

            # Electronics
            {
                'category': cat_objs['electronics'],
                'name': 'AlphaBook 14 Ultra Slim Laptop',
                'slug': 'alphabook-14-ultra-slim-laptop',
                'brand': 'AlphaTech',
                'short_description': '14-inch 2.8K OLED display, 16GB LPDDR5 RAM, 1TB NVMe SSD, aluminum chassis.',
                'description': 'Speed meets refinement. Powered by the latest 10-core high-efficiency processor, breathtaking 120Hz OLED screen with 100% DCI-P3 color gamut, backlit chiclet keyboard, glass trackpad, and Thunderbolt 4 connectivity.',
                'price': Decimal('1099.00'),
                'original_price': Decimal('1299.00'),
                'stock': 8,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'review_count': 55,
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['electronics'],
                'name': 'NeoKey Pro RGB Mechanical Keyboard',
                'slug': 'neokey-pro-rgb-mechanical-keyboard',
                'brand': 'AlphaTech',
                'short_description': 'Hot-swappable tactile switches, gasket-mounted acoustic dampening, PBT keycaps.',
                'description': 'An artisanal typing experience. Features CNC machined anodized aluminum body, factory-lubed custom switches, per-key dynamic RGB backlighting, tri-mode connectivity (2.4GHz / BT 5.0 / USB-C), and rotary volume knob.',
                'price': Decimal('129.99'),
                'original_price': Decimal('159.99'),
                'stock': 22,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'review_count': 31,
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['electronics'],
                'name': 'PrecisionGlide Ergonomic Wireless Mouse',
                'slug': 'precisionglide-ergonomic-wireless-mouse',
                'brand': 'AlphaTech',
                'short_description': 'Natural handshake grip, silent clicks, hyper-fast scroll wheel, 8000 DPI sensor.',
                'description': 'Reduce wrist strain during long coding and office hours. Features electromagnetic scroll wheel, thumb rest with gesture button, cross-computer control, and USB-C fast charging that lasts 70 days.',
                'price': Decimal('69.00'),
                'original_price': Decimal('89.00'),
                'stock': 35,
                'is_featured': False,
                'rating': Decimal('4.6'),
                'review_count': 22,
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['electronics'],
                'name': 'UltraView 27" 4K HDR Monitor',
                'slug': 'ultraview-27-4k-hdr-monitor',
                'brand': 'AlphaTech',
                'short_description': 'IPS panel, 99% sRGB, 65W USB-C charging, height-adjustable swivel stand.',
                'description': 'Elevate your visual workspace. Crystal clear 3840x2160 resolution with micro-edge bezels, HDR400 certified contrast, TÜV Rheinland eye comfort blue light filter, and one-cable USB-C display and laptop charging.',
                'price': Decimal('379.99'),
                'original_price': Decimal('449.99'),
                'stock': 12,
                'is_featured': False,
                'rating': Decimal('4.7'),
                'review_count': 18,
                'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80',
            },

            # Home & Workspace
            {
                'category': cat_objs['home-workspace'],
                'name': 'Lumen Brass Desk Lamp',
                'slug': 'lumen-brass-desk-lamp',
                'brand': 'AlphaLiving',
                'short_description': 'Architectural brushed brass finish, warm dimmable illumination, 360-degree swivel shade.',
                'description': 'Crafted with solid brushed brass and antique gold accents. The Lumen Brass Desk Lamp brings vintage sophistication and modern warmth to any workspace or bedside table. Features stepless rotary dimming, energy-saving LED warmth, heavy weighted anti-tip base, and a 360-degree adjustable swivel head.',
                'price': Decimal('79.99'),
                'original_price': Decimal('109.99'),
                'stock': 28,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'review_count': 26,
                'image_url': '/static/images/lumen_brass_desk_lamp.svg',
            },
            {
                'category': cat_objs['home-workspace'],
                'name': 'Barista Artisan Espresso Machine',
                'slug': 'barista-artisan-espresso-machine',
                'brand': 'AlphaLiving',
                'short_description': '19-bar Italian pump, commercial steam wand, pre-infusion pressure control.',
                'description': 'Craft velvety lattes and rich espresso at home. Features rapid thermoblock heating, stainless steel 54mm portafilter, dual wall filters, cup warming tray, and precision temperature stability.',
                'price': Decimal('249.99'),
                'original_price': Decimal('299.99'),
                'stock': 10,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'review_count': 29,
                'image_url': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['home-workspace'],
                'name': 'ZenFlow Wool Felt Desk Mat',
                'slug': 'zenflow-wool-felt-desk-mat',
                'brand': 'AlphaLiving',
                'short_description': 'Water-resistant natural merino wool blend desk pad with non-slip backing.',
                'description': 'Warm and tactile surface that cushions wrists and protects your desk. Generous 90cm x 40cm footprint accommodates keyboard, mouse, and laptop while maintaining an elegant workspace aesthetic.',
                'price': Decimal('29.99'),
                'original_price': Decimal('39.99'),
                'stock': 60,
                'is_featured': False,
                'rating': Decimal('4.6'),
                'review_count': 11,
                'image_url': 'https://images.unsplash.com/photo-1616401784845-180882ba9ba8?auto=format&fit=crop&w=800&q=80',
            },

            # Fashion & Lifestyle
            {
                'category': cat_objs['fashion-lifestyle'],
                'name': 'UrbanCommute Waterproof Daypack',
                'slug': 'urbancommute-waterproof-daypack',
                'brand': 'AlphaStyle',
                'short_description': 'Weatherproof Cordura fabric, padded 16" laptop sleeve, anti-theft zipper.',
                'description': 'Sleek geometric silhouette designed for modern tech commuters. Features dedicated tech organization compartments, luggage strap, breathable mesh back panel, and water bottle side pouch.',
                'price': Decimal('89.00'),
                'original_price': Decimal('119.00'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'review_count': 34,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['fashion-lifestyle'],
                'name': 'AeroStep Minimalist Knit Sneakers',
                'slug': 'aerostep-minimalist-knit-sneakers',
                'brand': 'AlphaStyle',
                'short_description': 'Breathable recycled yarn upper, cloud-foam responsive sole, lightweight.',
                'description': 'Engineered comfort for all-day walking. Moisture-wicking merino-blend lining, flexible grooved outsole for natural stride movement, and machine washable construction.',
                'price': Decimal('95.00'),
                'original_price': Decimal('125.00'),
                'stock': 18,
                'is_featured': False,
                'rating': Decimal('4.6'),
                'review_count': 23,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['fashion-lifestyle'],
                'name': 'Solace Polarized Aviator Sunglasses',
                'slug': 'solace-polarized-aviator-sunglasses',
                'brand': 'AlphaStyle',
                'short_description': 'Titanium alloy frames, UV400 anti-glare scratch resistant TAC lenses.',
                'description': 'Classic timeless teardrop design with modern durability. Features ultra-lightweight flexible temples, adjustable silicone nose pads, and 100% harmful UVA/UVB ray blocking.',
                'price': Decimal('49.00'),
                'original_price': Decimal('75.00'),
                'stock': 40,
                'is_featured': False,
                'rating': Decimal('4.5'),
                'review_count': 17,
                'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=800&q=80',
            },
            {
                'category': cat_objs['fashion-lifestyle'],
                'name': 'HydroFlask Insulated Thermal Bottle',
                'slug': 'hydroflask-insulated-thermal-bottle',
                'brand': 'AlphaStyle',
                'short_description': 'Double-wall vacuum insulation keeps drinks cold for 24h, hot for 12h. 750ml.',
                'description': 'Made of food-grade 18/8 pro stainless steel. Sweat-free powder coat finish, leak-proof wide mouth lid with flex handle, BPA-free, and fits standard car cup holders.',
                'price': Decimal('34.99'),
                'original_price': Decimal('42.00'),
                'stock': 55,
                'is_featured': False,
                'rating': Decimal('4.8'),
                'review_count': 28,
                'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80',
            },
        ]

        for p_data in products_data:
            p, created = Product.objects.update_or_create(
                slug=p_data['slug'],
                defaults=p_data
            )
            if created:
                # Add sample reviews
                ProductReview.objects.get_or_create(
                    product=p,
                    user=demo_user,
                    defaults={
                        'rating': 5,
                        'title': f'Superb quality! Exceeded my expectations',
                        'comment': f'I purchased this {p.name} two weeks ago and I am blown away by the craftsmanship and performance. Highly recommend!',
                    }
                )

        # 4. Create a sample order for demo user
        sample_prod = Product.objects.get(slug='alphawave-pro-wireless-headphones')
        order, ord_created = Order.objects.get_or_create(
            order_number='ORD-DEMO2026',
            defaults={
                'user': demo_user,
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1 (555) 234-5678',
                'address': '456 Tech Boulevard',
                'city': 'Austin',
                'state': 'Texas',
                'postal_code': '78701',
                'country': 'United States',
                'subtotal_amount': Decimal('189.99'),
                'shipping_amount': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'total_amount': Decimal('189.99'),
                'payment_method': 'card',
                'is_paid': True,
                'status': 'Processing',
                'order_notes': 'Please ring doorbell upon delivery.',
            }
        )
        if ord_created:
            OrderItem.objects.create(
                order=order,
                product=sample_prod,
                product_name=sample_prod.name,
                product_price=sample_prod.price,
                quantity=1,
                subtotal=sample_prod.price,
                image_url=sample_prod.image_url,
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(categories_data)} categories and {len(products_data)} products!"))
