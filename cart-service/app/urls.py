from django.urls import path
from .views import CartCreate, CartByCustomer, AddCartItem, UpdateCartItem, RemoveCartItem

urlpatterns = [
    path('carts/', CartCreate.as_view()),
    path('carts/<int:customer_id>/', CartByCustomer.as_view()),
    path('cart-items/', AddCartItem.as_view()),
    path('cart-items/<int:item_id>/', UpdateCartItem.as_view()),
    path('cart-items/<int:item_id>/remove/', RemoveCartItem.as_view()),
]