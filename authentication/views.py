from django.shortcuts import render,redirect
import os
from django.contrib.auth import get_user_model
import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
import time
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, logout
from django.contrib.auth import authenticate, login as auth_login 
from management.models import Categories,Product
from .models import Address,CartItem,Cart,Order,OrderItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash







# Create your views here.
def login_admin(request):
    print("THIS IS LOGIN_ADMIN")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser: 
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('users') 
            else:
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('login_admin') 
         
    return render(request,'admin1/login.html')

def generate_otp():
    return str(random.randint(100000, 999999))



def signup(request): 
    print("THIS IS SIGNUP")
    if request.user.is_authenticated:
        return redirect('home')
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.',extra_tags='signup-page')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.',extra_tags='signup-page')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.',extra_tags='signup-page')
        elif len(password1)<6:
            messages.error(request, 'Passwords must be six charecter.',extra_tags='signup-page')
        else:
            user = User(username=username, email=email)
            user.set_password(password1)
            otp = generate_otp()
            print("generated otp",otp)
            subject = 'Your OTP Code'
            message = f'Your OTP code is {otp}'
            from_email = settings.EMAIL_HOST_USER
            try:
                send_mail(subject, message, from_email, [email])
                request.session['otp'] = otp 
                request.session['otp_generated_time'] = time.time() 
                request.session['otp_expiration_time'] = 300
                request.session['resend_otp_time'] = 30   
                request.session['user_data'] = {'username': username, 'email': email, 'password': password1}
                return redirect('verify_otp')  
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}',extra_tags='signup-page')
                return render(request, 'user/otp.html',{'error': str(e)}) 
    return render(request,'user/signup.html')

def verify_otp(request):
    print("THIS IS VERIFY OTP")
    if request.user.is_authenticated:
        return redirect('home')
    User = get_user_model()

    if request.method == 'POST':
        otp_inputs = [
            request.POST.get('otp_1'),
            request.POST.get('otp_2'),
            request.POST.get('otp_3'),
            request.POST.get('otp_4'),
            request.POST.get('otp_5'),
            request.POST.get('otp_6'),
        ]
        entered_otp = ''.join(filter(None, otp_inputs))
        generated_otp = request.session.get('otp')
        user_data = request.session.get('user_data')
        print('Generated OTP:', generated_otp)
        print('Entered OTP:', entered_otp)
        otp_generated_time = request.session.get('otp_generated_time')
        otp_expiration_time = request.session.get('otp_expiration_time', 300)  
        current_time = time.time()
        if otp_generated_time is None:
            messages.error(request, 'No OTP generated. Please request a new one.')
            return redirect('request_otp')  
        if current_time - otp_generated_time > otp_expiration_time:
            messages.error(request, 'Your OTP has expired. Please request a new one.')
            return render(request, 'user/otp.html', context={'otp_form': True})
        if entered_otp == generated_otp:
            print('Valid OTP:', entered_otp)
            if user_data:
                user = User(username=user_data['username'], email=user_data['email'])
                user.set_password(user_data['password'])
                try:
                    user.full_clean()   
                    user.save()   
                    messages.success(request, 'Account created successfully!')
                    # login(request,user)
                    del request.session['otp']
                    del request.session['user_data']
                    return redirect('home')   
                except ValidationError as e:
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                messages.error(request, 'User data not found in session.')
        else:
            messages.error(request, 'Invalid OTP or expired OTP. Please try again.')
        return render(request, 'user/otp.html', context={'otp_form': True})
    return render(request, 'user/otp.html', context={'otp_form': True})


def resend_otp(request):
    print("RESEND OTP")
    User = get_user_model()

    if request.method == 'POST':
        last_resend_time = request.session.get('otp_generated_time', 0) + request.session.get('resend_otp_time', 0)
        email = request.session.get('user_data', {}).get('email')  
        if time.time() < last_resend_time:
            return JsonResponse({'status': 'error', 'message': 'Please wait before requesting a new OTP.'})
        email = request.session.get('user_data', {}).get('email')
        if not email:
            return JsonResponse({'status': 'error', 'message': 'User not found in session.'})
        otp = generate_otp() 
        subject = 'Your OTP Code'
        message = f'Your new OTP code is {otp}'
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, message, from_email, [email])
            request.session['otp'] = otp
            request.session['otp_generated_time'] = time.time()  
            request.session['otp_expiration_time'] = 300   
            return JsonResponse({'status': 'success', 'message': 'OTP has been resent.'})  
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})  
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}) 



def login(request):
    print("THIS IS LOGIN ")
    User = get_user_model() 
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('username:',username)
        print('password:',password)
        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'User does not exist. Please sign up.',extra_tags='login-page')
            return render(request, 'user/login.html', {'username': username})
        user = authenticate(request, username=username, password=password)
        print('user :',user)
        if user is not None:
              if not user.is_active:
                    messages.error(request, "You are not allowed to log in.",extra_tags='login-page')
                    return render(request, 'login.html')
              auth_login(request, user)
              return redirect('home')
        else:
            messages.error(request, 'Username or Password is wrong.',extra_tags='login-page')
            return render(request, 'user/login.html', {'username': username})
    return render(request,'user/login.html')


def home(request):
    catogery=Categories.objects.all()
    products=Product.objects.all()
    product = None
    if 'product_id' in request.GET:
        product_id = request.GET['product_id']
        product = get_object_or_404(Product, id=product_id)
    context={
        'catogery':catogery,
        'products':products,
         'product': product,
    }
    return render(request,'user/home.html',context)


def products(request):
    products=Product.objects.all()
    context={
        'products':products
    }
    return render(request,'user/products.html',context)

def products_detail(request,id):
    product = get_object_or_404(Product, id=id)
    context={
        'product':product
    }
    return render(request,'user/product_detail.html',context)


def cart(request):
    return render(request,'user/cart.html')


@never_cache 
@login_required(login_url='login')
def profile(request):
    user=request.user
    print(user)
    if user.is_authenticated:
        print(f"User is authenticated: {user.username}") 
    else:
        print("User is not authenticated")

    
    if request.method=='POST' and request.FILES.get('profile_picture'):
        profile_picture=request.FILES.get('profile_picture')
        user.profile_image=profile_picture
        user.save()
        return redirect('profile')
    print('user:', user)
    context={
         'user': user
    }
    return render(request,'user/profile.html',context)
def editprofile(request):
    user=request.user
    if request.method=='POST':
        user.email=request.POST.get('email')
        user.phone=request.POST.get('phone')
        user.dob=request.POST.get('dob')
        user.gender=request.POST.get('gender')
        user.city=request.POST.get('city')
        user.country=request.POST.get('country')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return render(request,'user/profile.html')

@never_cache
def change_password(request):
    error_messageprofile=None
    modal_open = False
    print('hii')
    if request.method=="POST":
        print('hlo')
        currentpassword=request.POST.get('current_password')
        newpasssword=request.POST.get('new_password')
        comfirmpassword=request.POST.get('confirm_password')
        
        if not request.user.check_password(currentpassword):
            error_messageprofile= "The current password is incorrect."
            modal_open = True
            print("error_messageprofile :",error_messageprofile)
            print('modal_open :',modal_open)
            return render(request, 'user/profile.html', {
                'error_messageprofile': error_messageprofile,
                'modal_open': modal_open
            })
        if newpasssword!=comfirmpassword:
            error_messageprofile= "The new passwords do not match."
            modal_open = True
            return render(request, 'user/profile.html', {
                'error_messageprofile': error_messageprofile,
                'modal_open': modal_open
            })
        if newpasssword:
            request.user.set_password('newpasssword')
            request.user.save()
            print('password changed')
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
        
        else:
            messages.error(request, "Please enter a valid new password.")
            return redirect('change_password')
    context={
        'error_messageprofile':error_messageprofile,
        'modal_open':modal_open
    }
    return render(request,'user/profile.html',context)

User = get_user_model()

@login_required(login_url='login')  
def address(request):
    address = Address.objects.filter(user=request.user, status='listed') 
    msg=None
    print('address:',address)
    print('user:',request.user)
    if request.method=='POST':
         
        user, created = User.objects.get_or_create(id=request.user.id)
        
        if created:
            messages.error(request, "User authentication issue. Please log in again.")
            return redirect('login')
 
        address_line1=request.POST.get('address_line1')
        city=request.POST.get('city')
        state=request.POST.get('state')
        postal_code=request.POST.get('postal_code')
        country=request.POST.get('country')
        phone_number=request.POST.get('phone_number')
        
        adress=Address.objects.create(user=request.user,address_line1=address_line1,city=city,state=state,postal_code=postal_code,country=country,phone_number=phone_number)
        msg='address created sucessfully!!!'
        return redirect('address')
    context={
        'address':address,
        'msg':msg
    }
    return render(request,'user/address.html',context)            
def editaddress(request,id):
    address = get_object_or_404(Address, id=id) 
    msg1=None
    if request.method=='POST':
       address.address_line1=request.POST.get('address_line1')
       address.city=request.POST.get('city')
       address.state=request.POST.get('state')
       address.postal_code=request.POST.get('postal_code')
       address.country=request.POST.get('country')
       address.phone_number=request.POST.get('phone_number')
       address.save()
       msg1='updated sucessfully'
       return redirect('address')
    context={
        'address':address,
        'msg1':msg1
    }
    return render(request,'user/address.html',context)
                
def listaddress(request,id):
    if request.method=='POST':
        address=get_object_or_404(Address,id=id)
        if address.status=='listed':
            address.status='dislisted'
         
        address.save()
        return redirect('address')  
    return render(request,'user/address.html')  


def brand_products(request, brand_name):
    products = Product.objects.filter(category__brand_name=brand_name)
    
    context = {
        'products': products,
        'brand_name': brand_name
    }
    
    return render(request, 'user/brand_products.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('num-product', 1))  
    cart, created = Cart.objects.get_or_create(user=request.user)

   
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if item_created:
        cart_item.quantity = quantity   
    else:
        cart_item.quantity += quantity  
    
    cart_item.save()   
    return redirect('cart_view')  

 
def cart_view(request):
    cart = Cart.objects.get(user=request.user)   
    cart_items = []   
    total_price = 0   

    for item in cart.items.all():
        item_total = item.product.price * item.quantity   
        total_price += item_total   
        cart_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'item_total': item_total,
        })

    addresses = Address.objects.filter(user=request.user)   

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'addresses': addresses,
    }

    if request.method == "POST":
        shipping_address_id = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')

        if not shipping_address_id or not payment_method:
            context['error'] = "Please select a shipping address and payment method."
            return render(request, 'user/cart.html', context)

       
        shipping_address = Address.objects.get(id=shipping_address_id)

   
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=total_price,
            payment_type=payment_method,
        )

   
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                subtotal_price=item.product.price * item.quantity,
            )

        
        cart.items.all().delete()

        return redirect('orders')   

    return render(request, 'user/cart.html', context) 

 

      
 
      
      
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(user=request.user)
    CartItem.objects.filter(cart=cart, product__id=product_id).delete()
    return redirect('cart_view')

def order(request):
    
    order_items = OrderItem.objects.all()   

    context = {
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'user/order.html', context)