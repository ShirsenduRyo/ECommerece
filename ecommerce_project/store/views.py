from django.shortcuts import render

from django.http import JsonResponse
import json
import datetime
from .models import *
# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cart_items = order.cart_items
    else:
        order = {'cart_total':0,'cart_items':0,'shipping':False}
        items = []
        cart_items = order['cart_items']
    
    products = Product.objects.all()

    context = {'products':products,'cart_items':cart_items}

    return render(request,"store/store.html",context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cart_items = order.cart_items
    else:
        order = {'cart_total':0,'cart_items':0,'shipping':False}
        items = []
        cart_items = order['cart_items']

    context = {'items':items,'order':order,'cart_items':cart_items}

    return render(request,"store/cart.html",context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cart_items = order.cart_items
    else:
        order = {'cart_total':0,'cart_items':0, 'shipping':False}
        items = []
        cart_items = order['cart_items']

    context = {'items':items,'order':order,'cart_items':cart_items}
    
    return render(request,"store/checkout.html",context)

def update_item(request):
    data = json.loads(request.body)
    
    product_id = data["product_id"]
    action = data["action"]
    print("action:",action)
    print("product_id:",product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer = customer,complete = False)

    order_item, created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == "add":
        order_item.quantity += 1
    elif action == "remove":
        order_item.quantity -= 1 

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse("Item was Added", safe=False)

def process_order(request):
    transaction_id= datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer 
    
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
    
        # To make sure the user didnt manipulated the data
        if total == order.cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )

    else:
        print("User is not Authenticated")

    print("Data:",request.body)
    return JsonResponse("Payment Complete! ", safe=False)