import json
from .models import *

def cookie_cart(request):
    cart = json.loads(request.COOKIES['cart'])
    print('Cart:',cart)

    order = {'cart_total':0,'cart_items':0,'shipping':False}
    items = []
    cart_items = order['cart_items']

    for p_id in cart:
        # If the product in the cart gets deleted from the database
        try:
            cart_items += cart[p_id]["quantity"] 

            product = Product.objects.get(id = p_id)
            total = product.price * cart[p_id]["quantity"] 

            order['cart_total'] += total
            order['cart_items'] += cart[p_id]["quantity"] 

            item  = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image_url':product.image_url,
                },
            'quantity': cart[p_id]["quantity"] ,
            'get_total':total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass

    return {'cart_items':cart_items ,'order':order, 'items':items}

def cookie_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,complete = False)
        items = order.orderitem_set.all()
        cart_items = order.cart_items
    else:
        cookie_data = cookie_cart(request)
        items = cookie_data['items']
        order = cookie_data['order']
        cart_items = cookie_data['cart_items']

    return {'items':items,'order':order,'cart_items':cart_items}


def guest_order(request,data):
    print("User is not Authenticated")
    print('Cookies:',request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']

    cookie_datum = cookie_cart(request)
    items = cookie_datum['items']

    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    for item in items:
        product = Product.objects.get(id = item['product']['id'])

        order_item = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        )
    
    return customer, order