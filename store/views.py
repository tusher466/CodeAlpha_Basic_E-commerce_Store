import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Category, Product, Cart, CartItem, Order, OrderItem, ProductReview, UserProfile
from .forms import UserRegisterForm, CheckoutForm, ReviewForm, UserInfoForm
from .context_processors import get_or_create_cart


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    categories = Category.objects.all()

    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.filter(is_available=True)
    category_slug = request.GET.get('category')
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    # Pagination: 9 per page
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'current_category': current_category,
        'query': query,
        'sort_by': sort_by,
        'total_results': paginator.count,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to submit a review.")
            return redirect('store:login')
        
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            # Recalculate product rating
            all_ratings = [r.rating for r in product.reviews.all()]
            product.rating = Decimal(sum(all_ratings) / len(all_ratings))
            product.review_count = len(all_ratings)
            product.save()

            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('store:product_detail', slug=product.slug)

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)


def cart_detail(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    subtotal = cart.get_subtotal()
    shipping = cart.get_shipping()

    # Coupon handling from session
    coupon_code = request.session.get('coupon_code', '')
    discount_percent = request.session.get('coupon_discount', 0)
    
    discount_amount = Decimal('0.00')
    if discount_percent > 0:
        discount_amount = (subtotal * Decimal(discount_percent) / Decimal(100)).quantize(Decimal('0.01'))

    total = subtotal + shipping - discount_amount
    if total < Decimal('0.00'):
        total = Decimal('0.00')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount_amount': discount_amount,
        'coupon_code': coupon_code,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    quantity = 1
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    # Check stock limit
    if cart_item.quantity > product.stock:
        cart_item.quantity = max(1, product.stock)
        messages.warning(request, f"Limited to available stock ({product.stock} items).")
    cart_item.save()

    # AJAX Response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': f'"{product.name}" added to your cart!',
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_subtotal()),
        })

    messages.success(request, f'"{product.name}" was added to your shopping cart.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'store:cart_detail'
    return redirect(next_url)


def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            qty = int(request.POST.get('quantity', cart_item.quantity))
        except (ValueError, TypeError):
            qty = cart_item.quantity

        if action == 'increase':
            qty = cart_item.quantity + 1
        elif action == 'decrease':
            qty = cart_item.quantity - 1

        if qty <= 0:
            cart_item.delete()
        else:
            if qty > cart_item.product.stock:
                qty = cart_item.product.stock
                messages.warning(request, f"Only {cart_item.product.stock} units available in stock.")
            cart_item.quantity = qty
            cart_item.save()

    # AJAX Response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subtotal = float(cart.get_subtotal())
        shipping = float(cart.get_shipping())
        discount_percent = request.session.get('coupon_discount', 0)
        discount_amount = round(subtotal * (discount_percent / 100), 2)
        total = round(max(0.0, subtotal + shipping - discount_amount), 2)

        item_subtotal = float(cart_item.get_subtotal()) if CartItem.objects.filter(id=item_id).exists() else 0.0

        return JsonResponse({
            'status': 'success',
            'item_quantity': cart_item.quantity if CartItem.objects.filter(id=item_id).exists() else 0,
            'item_subtotal': item_subtotal,
            'cart_count': cart.get_total_items(),
            'subtotal': subtotal,
            'shipping': shipping,
            'discount': discount_amount,
            'total': total,
        })

    return redirect('store:cart_detail')


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subtotal = float(cart.get_subtotal())
        shipping = float(cart.get_shipping())
        discount_percent = request.session.get('coupon_discount', 0)
        discount_amount = round(subtotal * (discount_percent / 100), 2)
        total = round(max(0.0, subtotal + shipping - discount_amount), 2)

        return JsonResponse({
            'status': 'success',
            'message': f'"{product_name}" removed from cart.',
            'cart_count': cart.get_total_items(),
            'subtotal': subtotal,
            'shipping': shipping,
            'discount': discount_amount,
            'total': total,
        })

    messages.info(request, f'"{product_name}" was removed from your cart.')
    return redirect('store:cart_detail')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        coupons = {
            'ALPHA10': 10,
            'CODEALPHA': 15,
            'WELCOME20': 20,
        }

        if code in coupons:
            request.session['coupon_code'] = code
            request.session['coupon_discount'] = coupons[code]
            messages.success(request, f'Coupon "{code}" applied! You saved {coupons[code]}%.')
        else:
            messages.error(request, 'Invalid promotional coupon code.')

    return redirect('store:cart_detail')


def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    messages.info(request, "Coupon removed.")
    return redirect('store:cart_detail')


def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add products before checking out.")
        return redirect('store:product_list')

    subtotal = cart.get_subtotal()
    shipping = cart.get_shipping()
    coupon_code = request.session.get('coupon_code', '')
    discount_percent = request.session.get('coupon_discount', 0)
    discount_amount = Decimal('0.00')

    if discount_percent > 0:
        discount_amount = (subtotal * Decimal(discount_percent) / Decimal(100)).quantize(Decimal('0.01'))

    total = subtotal + shipping - discount_amount
    if total < Decimal('0.00'):
        total = Decimal('0.00')

    # Initial form data from authenticated user if available
    initial_data = {}
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country or 'United States',
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            
            order.subtotal_amount = subtotal
            order.shipping_amount = shipping
            order.discount_amount = discount_amount
            order.total_amount = total
            order.coupon_code = coupon_code
            order.status = 'Processing'

            # Payment simulation
            if order.payment_method in ['card', 'paypal']:
                order.is_paid = True
            else:
                order.is_paid = False

            order.save()

            # Create OrderItems and decrement stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    subtotal=item.get_subtotal(),
                    image_url=item.product.image_url
                )
                # Deduct stock safely
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                else:
                    item.product.stock = 0
                item.product.save()

            # Clear cart items and coupon
            cart.items.all().delete()
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            if 'coupon_discount' in request.session:
                del request.session['coupon_discount']

            request.session['last_order_id'] = order.id
            messages.success(request, f"Order #{order.order_number} placed successfully!")
            return redirect('store:order_success', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount_amount': discount_amount,
        'total': total,
        'coupon_code': coupon_code,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        'order': order,
    }
    return render(request, 'store/order_success.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'store/orders.html', context)


def order_detail(request, order_number):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, order_number=order_number)
        # Check permissions: if not staff and order belongs to another user, restrict
        if not request.user.is_staff and order.user and order.user != request.user:
            messages.error(request, "Access denied to this order.")
            return redirect('store:home')
    else:
        # Check if it was placed in this session
        order = get_object_or_404(Order, order_number=order_number)

    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)


def user_register(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request, "Registration successful! You are now logged in.")
            login(request, user, backend='store.backends.EmailOrUsernameModelBackend')

            # Claim session cart
            if request.session.session_key:
                Cart.objects.filter(session_key=request.session.session_key).update(user=user)

            return redirect('store:home')
    else:
        form = UserRegisterForm()

    return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.GET.get('role') == 'admin':
            return redirect('/admin/')
        return redirect('store:home')

    # One-click quick login handler for demo convenience
    if request.method == 'POST' and 'quick_login' in request.POST:
        role = request.POST.get('quick_login')
        username = 'admin' if role == 'admin' else 'johndoe'
        pwd = 'admin123' if role == 'admin' else 'password123'

        user = authenticate(request, username=username, password=pwd)
        if not user:
            # Guarantee user exists and active
            u = User.objects.filter(username=username).first()
            if u:
                u.set_password(pwd)
                u.is_active = True
                if role == 'admin':
                    u.is_staff = True
                    u.is_superuser = True
                u.save()
            else:
                if role == 'admin':
                    u = User.objects.create_superuser('admin', 'admin@codealpha.tech', 'admin123')
                else:
                    u = User.objects.create_user('johndoe', 'john@example.com', 'password123')
            user = authenticate(request, username=username, password=pwd)

        if user:
            login(request, user)
            if user.is_staff:
                messages.success(request, "Signed in successfully as Administrator with full admin dashboard access.")
                return redirect('/admin/')
            else:
                messages.success(request, f"Signed in successfully as {user.first_name or user.username}!")
                return redirect('store:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Claim session cart
            if request.session.session_key:
                guest_cart = Cart.objects.filter(session_key=request.session.session_key, user=None).first()
                if guest_cart:
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    for item in guest_cart.items.all():
                        existing = CartItem.objects.filter(cart=user_cart, product=item.product).first()
                        if existing:
                            existing.quantity += item.quantity
                            existing.save()
                        else:
                            item.cart = user_cart
                            item.save()
                    guest_cart.delete()

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if not next_url:
                if user.is_staff or user.is_superuser:
                    return redirect('/admin/')
                next_url = 'store:home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password. Please verify your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})



def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('store:home')


@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'profile': profile,
    }
    return render(request, 'store/profile.html', context)


@login_required
def user_info(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            profile.phone = form.cleaned_data['phone']
            profile.address = form.cleaned_data['address']
            profile.city = form.cleaned_data['city']
            profile.state = form.cleaned_data['state']
            profile.postal_code = form.cleaned_data['postal_code']
            profile.country = form.cleaned_data['country'] or 'United States'
            profile.save()

            messages.success(request, "Your personal information and address details have been updated successfully.")
            return redirect('store:user_info')
    else:
        form = UserInfoForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country or 'United States',
        })

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'store/user_info.html', context)

