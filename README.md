# CodeAlpha E-Commerce Web Application

A full-stack, responsive, and feature-rich E-Commerce Web Platform created for the **CodeAlpha** Web Development Task ([www.codealpha.tech](https://www.codealpha.tech)).

---

## 🌟 Key Features

### 🛍️ 1. Product Listings & Catalog
- **Interactive Catalog**: Browse products with live filtering by category, search queries, and sorting (Newest, Price: Low to High, Price: High to Low, Rating, Alphabetical).
- **Product Cards**: Display high-resolution photography, discount badges (`-20%`), stock status, ratings, brand tag, and quick **AJAX Add to Cart** without page reload.
- **Dynamic Category Navigation**: Categories with product counters and quick access from header/subnav.

### 🔍 2. Product Details Page (`/products/<slug>/`)
- **Breadcrumb Navigation**: Clear path back to Home and Category.
- **Detailed View**: Product gallery, price, original crossed-out price, stock status, and short summary.
- **Interactive Quantity Stepper**: Increments/decrements quantity with stock limit guards.
- **Add to Cart & Instant Toast**: Responsive feedback via custom animated toast notifications.
- **Customer Reviews & Ratings**: Displays average star ratings, customer feedback history, and an interactive submission form for authenticated users.
- **Related Products Carousel**: Automatic suggestions from the same category.

### 🛒 3. Shopping Cart System (`/cart/`)
- **Persistent Cart**: Works seamlessly for both guest users (session-based) and logged-in users (database-backed), automatically merging guest carts upon login.
- **Live Quantity Controls**: Update item quantities (+ / - / direct input) and delete items with instant AJAX DOM updates.
- **Free Shipping Calculator**: Dynamic progress bar indicating how close the customer is to unlocking free shipping ($50 threshold).
- **Promo Coupon System**: Apply promotional discount codes (e.g., `ALPHA10` for 10% off, `WELCOME20` for 20% off).

### 💳 4. Order Processing & Checkout (`/checkout/`)
- **Shipping Address Form**: Full Name, Email, Phone, Street Address, City, State, Postal Code, Country, and Delivery Notes. Pre-filled automatically for logged-in accounts.
- **Multiple Payment Methods**:
  - Cash on Delivery (COD)
  - Simulated Credit/Debit Card with interactive card details
  - Digital Wallet / PayPal (Demo)
- **Automatic Stock Deduction**: Product inventory is safely decremented upon successful order placement.
- **Order Confirmation Page (`/orders/success/<order_number>/`)**:
  - Unique order tracking code (e.g. `ORD-XXXXXXXXXX`)
  - Itemized receipt breakdown (Product, Quantity, Price, Subtotal, Shipping, Discount, Total)
  - **Print Invoice** button formatted for printing and PDF generation.

### 🔐 5. User Registration, Authentication & Profile
- **Registration (`/register/`)**: New user signup with password validation and email uniqueness checking.
- **Login (`/login/`)**: Session-based login with demo account suggestions.
- **Customer Dashboard (`/profile/`)**: Overview of account information, active status, order count, and quick links.
- **Order History (`/orders/`)**: Complete timeline of past orders with tracking status badges (`Pending`, `Processing`, `Shipped`, `Delivered`).
- **Order Detail Invoice (`/orders/<order_number>/`)**: Full order tracking with interactive 4-stage delivery progress bar.

### 🛠️ 6. Django Admin Portal (`/admin/`)
- Manage Categories, Products, Inventory, Stock levels, Orders, Order items, and Reviews.
- Search, filter, and modify order status (`Pending`, `Processing`, `Shipped`, `Delivered`, `Cancelled`) directly.

---

## 🏗️ Technology Stack

| Component | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Modern Vanilla JavaScript (Fetch API, DOM manipulation) |
| **Styling** | Bootstrap 5.3.3 + Custom CSS Variables + Bootstrap Icons |
| **Backend** | Python 3.12 + Django 5.1.6 (MTV Architecture) |
| **Database** | SQLite (Zero-configuration, built-in ORM) |
| **Testing** | Django Test Framework (Unit & Integration tests) |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed on your computer.

### 2. Launching the Application
You can launch the server using either the provided launch scripts or standard terminal commands:

#### Option A: One-Click Launch Script
- **Windows (Double-click or CMD)**:
  ```cmd
  run_server.bat
  ```
- **PowerShell**:
  ```powershell
  .\run_server.ps1
  ```

#### Option B: Manual Command Line
```powershell
# Activate the virtual environment
.\.venv\Scripts\activate

# (Optional) Seed fresh data if needed
python manage.py seed_data

# Run the development server
python manage.py runserver 127.0.0.1:8000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Pre-Seeded Demo Accounts

The project includes pre-configured demo accounts ready for testing:

| Role | Username / Email | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` OR `admin@codealpha.tech` | `admin123` (or `admin`) | Full access to `/admin/` portal |
| **Customer** | `johndoe` OR `john@example.com` | `password123` | Has pre-existing order and reviews |

> **Tip:** You can also use the 1-Click Instant Login button on the [Login Page](http://127.0.0.1:8000/login/) to sign in as Administrator directly with a single click.

---

## 🏷️ Test Coupons

Enter any of these codes in the Shopping Cart or Checkout:
- `ALPHA10` — 10% Discount
- `CODEALPHA` — 15% Discount
- `WELCOME20` — 20% Discount

---

## 🧪 Running Automated Tests

Run the complete test suite verifying models, views, cart operations, AJAX endpoints, checkout flow, and authentication:

```powershell
.\.venv\Scripts\python.exe manage.py test store
```

Expected result:
```
Ran 9 tests in 3.607s
OK
```

---

## 📁 Project Directory Structure

```
d:\Task 1\
├── ecommerce_project/          # Django project configuration
│   ├── settings.py             # Settings, apps, static & media definitions
│   ├── urls.py                 # Main URL router
│   ├── wsgi.py
│   └── asgi.py
├── store/                      # Main e-commerce application
│   ├── models.py               # Category, Product, Cart, CartItem, Order, OrderItem, Review
│   ├── views.py                # Controller logic & AJAX handlers
│   ├── forms.py                # Register, Checkout, and Review forms
│   ├── urls.py                 # Store route declarations
│   ├── admin.py                # Django admin customizations
│   ├── context_processors.py   # Global cart & navigation context
│   ├── tests.py                # Unit & integration test cases
│   └── management/commands/
│       └── seed_data.py        # Database seeding command
├── templates/
│   └── store/                  # HTML templates
│       ├── base.html           # Master layout & navbar
│       ├── home.html           # Homepage & hero banner
│       ├── product_list.html   # Catalog & filters
│       ├── product_detail.html # Product details & reviews
│       ├── cart.html           # Interactive shopping cart
│       ├── checkout.html       # Order checkout form
│       ├── order_success.html  # Order confirmation & receipt
│       ├── orders.html         # User order history
│       ├── order_detail.html   # Detailed order invoice & tracker
│       ├── login.html          # User login
│       ├── register.html       # User registration
│       └── profile.html        # Account profile dashboard
├── static/
│   ├── css/
│   │   └── style.css           # Custom styles & design system
│   └── js/
│       └── main.js             # AJAX cart, toasts, quantity steppers
├── db.sqlite3                  # SQLite Database
├── manage.py
├── requirements.txt
├── run_server.bat
├── run_server.ps1
└── README.md
```

---

## 🏢 Attribution
Developed as part of the Web Development Internship program at **CodeAlpha** ([www.codealpha.tech](https://www.codealpha.tech)).
