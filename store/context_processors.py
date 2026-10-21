from .models import Category, Cart


def get_or_create_cart(request):
    """Utility to retrieve or create the user or session cart."""
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            # Check if there is an anonymous session cart to claim
            cart = Cart.objects.filter(session_key=session_key).first()
            if cart:
                cart.user = request.user
                cart.save()
            else:
                cart = Cart.objects.create(user=request.user, session_key=session_key)
        return cart
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, defaults={'user': None})
        return cart


def store_context(request):
    """Context processor available in all templates."""
    categories = Category.objects.all()
    cart_item_count = 0
    cart_subtotal = 0.00
    cart = None

    try:
        if hasattr(request, 'session'):
            cart = get_or_create_cart(request)
            cart_item_count = cart.get_total_items()
            cart_subtotal = cart.get_subtotal()
    except Exception:
        pass

    return {
        'all_categories': categories,
        'global_cart': cart,
        'cart_item_count': cart_item_count,
        'cart_subtotal': cart_subtotal,
        'SITE_NAME': 'CodeAlpha Commerce',
        'SITE_DOMAIN': 'www.codealpha.tech',
    }
