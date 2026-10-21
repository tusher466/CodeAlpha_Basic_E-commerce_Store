from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order, OrderItem, ProductReview


class EcommerceSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Audio Tech",
            slug="audio-tech",
            description="High quality headphones"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Alpha Sound Pro",
            slug="alpha-sound-pro",
            brand="AlphaSound",
            short_description="Great audio gear",
            description="Deep noise canceling bass and studio quality sound.",
            price=Decimal("100.00"),
            original_price=Decimal("120.00"),
            stock=15,
            is_available=True,
            is_featured=True,
            image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123"
        )

    def test_product_model_properties(self):
        """Test product discount calculation and stock availability"""
        self.assertTrue(self.product.is_in_stock)
        self.assertEqual(self.product.discount_percent, 17)  # (120 - 100) / 120 * 100 = 16.66% -> 17%
        self.assertEqual(str(self.product), "Alpha Sound Pro")

    def test_home_page(self):
        """Test home view returns 200 and renders products"""
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Sound Pro")
        self.assertContains(response, "CodeAlpha")

    def test_product_catalog_and_search(self):
        """Test product list page and search filtering"""
        # All products
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Sound Pro")

        # Search matching query
        response_search = self.client.get(reverse('store:product_list') + '?q=Alpha')
        self.assertContains(response_search, "Alpha Sound Pro")

        # Search non-matching query
        response_empty = self.client.get(reverse('store:product_list') + '?q=NonExistentProductXYZ')
        self.assertContains(response_empty, "No products found")

    def test_product_detail_page(self):
        """Test product detail page displays correct information"""
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Sound Pro")
        self.assertContains(response, "$100.00")
        self.assertContains(response, "In Stock")

    def test_cart_operations(self):
        """Test adding to cart, updating quantity, and removing item"""
        # 1. Add to cart
        add_url = reverse('store:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {'quantity': 2})
        self.assertEqual(response.status_code, 302)

        # 2. View Cart
        cart_page = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(cart_page.status_code, 200)
        self.assertContains(cart_page, "Alpha Sound Pro")
        self.assertContains(cart_page, "$200.00")  # 2 * 100

        # 3. Update quantity
        cart = Cart.objects.first()
        cart_item = cart.items.first()
        self.assertEqual(cart_item.quantity, 2)

        update_url = reverse('store:update_cart', kwargs={'item_id': cart_item.id})
        self.client.post(update_url, {'action': 'increase'})
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

        # 4. Remove from cart
        remove_url = reverse('store:remove_from_cart', kwargs={'item_id': cart_item.id})
        self.client.post(remove_url)
        self.assertEqual(cart.items.count(), 0)

    def test_ajax_add_to_cart(self):
        """Test JSON AJAX add to cart response"""
        add_url = reverse('store:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(
            add_url,
            {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['cart_count'], 1)

    def test_coupon_application(self):
        """Test coupon discount logic"""
        # Add item to cart
        self.client.post(reverse('store:add_to_cart', kwargs={'product_id': self.product.id}), {'quantity': 1})
        
        # Apply valid coupon
        response = self.client.post(reverse('store:apply_coupon'), {'coupon_code': 'ALPHA10'})
        self.assertEqual(response.status_code, 302)

        cart_page = self.client.get(reverse('store:cart_detail'))
        self.assertContains(cart_page, "ALPHA10 Applied")

    def test_checkout_and_order_processing(self):
        """Test full checkout flow: cart to order creation, stock deduction, and order receipt"""
        # 1. Add item to cart
        self.client.post(reverse('store:add_to_cart', kwargs={'product_id': self.product.id}), {'quantity': 2})
        initial_stock = self.product.stock

        # 2. Submit checkout form
        checkout_data = {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '+1 555-1234',
            'address': '789 Market Street',
            'city': 'Seattle',
            'state': 'WA',
            'postal_code': '98101',
            'country': 'United States',
            'payment_method': 'card',
            'order_notes': 'Leave at front door please.'
        }
        response = self.client.post(reverse('store:checkout'), checkout_data)
        
        # Should redirect to order success
        self.assertEqual(response.status_code, 302)
        order = Order.objects.filter(email='alice@example.com').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.status, 'Processing')
        self.assertTrue(order.is_paid)

        # Verify stock was deducted
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)

        # 3. View order confirmation
        success_url = reverse('store:order_success', kwargs={'order_number': order.order_number})
        success_page = self.client.get(success_url)
        self.assertEqual(success_page.status_code, 200)
        self.assertContains(success_page, order.order_number)
        self.assertContains(success_page, "Thank You For Your Order")

    def test_user_authentication_flow(self):
        """Test registration, login, profile view, and logout"""
        # Register
        register_data = {
            'username': 'newuser123',
            'first_name': 'New',
            'last_name': 'Person',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        reg_response = self.client.post(reverse('store:register'), register_data)
        self.assertEqual(reg_response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser123').exists())

        # Access profile while logged in
        profile_page = self.client.get(reverse('store:profile'))
        self.assertEqual(profile_page.status_code, 200)
        self.assertContains(profile_page, "newuser123")

        # Logout
        logout_response = self.client.get(reverse('store:logout'))
        self.assertEqual(logout_response.status_code, 302)

        # Login
        login_response = self.client.post(reverse('store:login'), {
            'username': 'newuser123',
            'password': 'StrongPassword123!'
        })
        self.assertEqual(login_response.status_code, 302)

    def test_user_information_page(self):
        """Test user information page displays and updates profile details"""
        self.client.login(username="testuser", password="testpassword123")
        
        # 1. GET user info
        response = self.client.get(reverse('store:user_info'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")

        # 2. POST update user info
        update_data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@example.com',
            'phone': '+1 (555) 999-8888',
            'address': '100 Silicon Way',
            'city': 'San Jose',
            'state': 'CA',
            'postal_code': '95113',
            'country': 'United States',
        }
        post_response = self.client.post(reverse('store:user_info'), update_data)
        self.assertEqual(post_response.status_code, 302)

        # Verify User and Profile updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.profile.phone, '+1 (555) 999-8888')
        self.assertEqual(self.user.profile.city, 'San Jose')

    def test_admin_authentication_and_quick_login(self):
        """Test admin login via credentials and quick 1-click button"""
        admin = User.objects.create_superuser('adminuser', 'adminuser@codealpha.tech', 'adminpass123')

        # 1. Login with username
        resp1 = self.client.post(reverse('store:login'), {
            'username': 'adminuser',
            'password': 'adminpass123'
        })
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(resp1.url, '/admin/')
        self.client.logout()

        # 2. Login with email
        resp2 = self.client.post(reverse('store:login'), {
            'username': 'adminuser@codealpha.tech',
            'password': 'adminpass123'
        })
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2.url, '/admin/')
        self.client.logout()

        # 3. Quick 1-click admin login
        resp3 = self.client.post(reverse('store:login'), {
            'quick_login': 'admin'
        })
        self.assertEqual(resp3.status_code, 302)
        self.assertEqual(resp3.url, '/admin/')


