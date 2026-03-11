from django.urls import path, re_path
from gateway import views

urlpatterns = [

    # ── PUBLIC ──────────────────────────────────────────
    path('login/',          views.login_view,      name='login'),
    path('auth/login/',     views.api_login,       name='api_login'),
    path('logout/',         views.logout_view,     name='logout'),
    path('customers/new/',  views.create_customer, name='create_customer'),
    path('health/',         views.health_check,    name='health'),

    # ── CUSTOMER ────────────────────────────────────────
    path('',                views.home,            name='home'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('cart/',           views.my_cart,         name='my_cart'),
    path('cart/add/',       views.add_to_cart,     name='add_to_cart'),
    path('cart/remove/',    views.remove_from_cart, name='remove_from_cart'),
    path('cart/<int:customer_id>/', views.view_cart, name='view_cart'),
    path('checkout/',       views.checkout,        name='checkout'),

    # ── STAFF ───────────────────────────────────────────
    path('staff/',          views.staff_dashboard, name='staff_dashboard'),
    path('staff/books/',    views.book_list,       name='book_list'),
    path('staff/books/<int:book_id>/edit/',   views.book_edit,   name='book_edit'),
    path('staff/books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('staff/comments/', views.staff_comments,  name='staff_comments'),

    # ── MANAGER/ADMIN ───────────────────────────────────
    path('dashboard/',      views.dashboard,       name='dashboard'),
    path('admin/users/',    views.admin_users,     name='admin_users'),
    path('orders/new/',     views.create_order,    name='create_order'),

    # ── API PROXY ───────────────────────────────────────
    re_path(r'^api/(?P<service>[^/]+)/(?P<path>.*)$', views.proxy),
]