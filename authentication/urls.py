"""
URL configuration for tinytires project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('login_admin/',views.login_admin,name='login_admin'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('products/',views.products,name='products'),
    path('profile/',views.profile,name='profile'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('products_detail/',views.products_detail,name='products_detail'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('product/<int:id>/', views.products_detail, name='product_detail'),
    path('change_password/',views.change_password,name='change_password'),
    path('address/',views.address,name='address'),
    path('editaddress/<int:id>/',views.editaddress,name='editaddress'),
    path('listaddress/<int:id>/',views.listaddress,name='listaddress'),
    path('products/brand/<str:brand_name>/', views.brand_products, name='brand_products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'), 
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('order_summary/', views.order, name='orders'),


  ]
