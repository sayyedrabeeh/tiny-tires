from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from management.models import Product
from django.contrib.auth import get_user_model
from django.conf import settings  
import uuid
from datetime import timedelta  
from django.utils import timezone 
from management.models import Product

  

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', default='images/profile.png')
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',   
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',   
        blank=True,
    )
    
    def __str__(self):
        return self.username if self.username else "Unnamed User"
 
User = get_user_model()


class Address(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    status  =models.CharField(default='listed')


    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state} - {self.postal_code}"

    class Meta:
        verbose_name_plural = "Addresses"
        
        
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('RazorPay', 'Razor Pay'),
        ('Wallet', 'Wallet')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failure', 'Failure')
    ]

    order_id = models.AutoField(primary_key=True)  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=20, unique=True, editable=False)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    estimated_delivery_date = models.DateField(blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.order_id} by {self.user.username}'

    def save(self, *args, **kwargs):
         
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4().hex[:8])
        if not self.estimated_delivery_date:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=3)   
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ("Order Pending", "Order Pending"),
        ("Order Confirmed", "Order Confirmed"),
        ("Shipped", "Shipped"),
        ("Out For Delivery", "Out For Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Requested Return", "Requested Return"),
        ("Approve Returned", "Approve Returned"),
        ("Reject Returned", "Reject Returned"),
    ]
    
    orderitem_id = models.AutoField(primary_key=True)  
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order Pending') 
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    return_reason = models.TextField(blank=True, null=True)
    product = models.ForeignKey('management.Product', on_delete=models.CASCADE)  # Correct reference
    
  
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE )
    quantity = models.PositiveIntegerField(default=1)

    def item_total(self):
        return self.product.price * self.quantity 


    def __str__(self):
        return f"{self.variant} (x{self.quantity})"
    
    
