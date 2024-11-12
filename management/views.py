from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from .models import Categories, Product, ProductImage
from authentication.models import OrderItem,Order

# Create your views here.
User = get_user_model()


def users(request):
    User = get_user_model()
    users=User.objects.all()
    context={
        'users':users
    }
    return render(request,'admin1/users.html',context)


def catogery(request):
    print('hi')
    error_message = None
    modal_open = False
    categories = Categories.objects.all()
    if request.method=='POST':
        image=request.FILES.get('catogeryimage')
        name=request.POST.get('name')
        status=request.POST.get('status')
        
        if Categories.objects.filter(brand_name=name).exists():
             error_message = "Category with this name already exists!"
             modal_open = True
        else:
            catogery=Categories.objects.create(brand_name=name,active=status,image=image)
            return redirect('catogery')
    print('error_message:',categories)
    context={
       'categories': categories,
       'error_message':error_message,
       'modal_open':modal_open 
    }
    return render(request,'admin1/catogery.html',context)
def edit_catogery(request,id):
    catogery=get_object_or_404(Categories,id=id)
    
    if request.method=='POST':
        name=request.POST.get('brand_name')
        active=request.POST.get('active') 
        image=request.FILES.get('image')
        catogery.brand_name=name
        catogery.active=active
        if image:
            catogery.image=image
        
        catogery.save()
        print('catogery:',catogery)
        return redirect('catogery')
      
    return render(request,'admin1/catogery.html')
def catogerylist(request,id):
    if request.method=='POST':
        catogery=get_object_or_404(Categories,id=id)
        if catogery.status=='listed':
            catogery.status='dislisted'
        else:
            catogery.status='listed'
        catogery.save()
        return redirect('catogery')
        
def products(request):
    categories = Categories.objects.all()
    products=Product.objects.all()
    if request.method=='POST':
        product_name=request.POST.get('product_name')
        size=request.POST.get('size')
        price=request.POST.get('price')
        stock=request.POST.get('stock')
        description=request.POST.get('description')
        images=request.FILES.getlist('images')
        category_id = request.POST.get('category')  
        category = Categories.objects.get(id=category_id) if category_id else None
        products=Product.objects.create(name=product_name,description=description,size=size,price=price,stock=stock,category=category)
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                ProductImage.objects.create(product=products, image=image)
            return redirect('products')
    context={
        'categories':categories,
        'products':products
    } 
    return render(request,'admin1/products.html',context)

def productlist(request,id):
    if request.method=='POST':
        products=get_object_or_404(Product,id=id)
        if products.status=='listed':
            products.status='dislisted'
        else:
            products.status='listed'
        products.save()
        return redirect('products')
    
def blockuser(request,id):
    user=User.objects.get(id=id)
    user.is_active=not user.is_active
    user.save()
    return redirect('users')

def order(request):
    orders = Order.objects.all()  

    context = {
        'orders': orders,
    }
    return render(request,'admin1/order.html',context)

def get_order_items(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all()  # Retrieve all order items for this order
    
    # Prepare the data to send in the response
    order_items_data = []
    for item in order_items:
        order_items_data.append({
            'product': {
                'name': item.product.name,
                'image_url': item.product.image.url if item.product.image else '',
            },
            'quantity': item.quantity,
            'status': item.status,
            'subtotal_price': item.product.price * item.quantity,
            'shipping_address': order.shipping_address.address,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'order_items': order_items_data})