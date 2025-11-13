from itertools import product
from cart.models import Order_items
from django.shortcuts import render,redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from cart.models import Cart
import uuid

from shop.models import Products
import razorpay
class AddtoCart(View):
    def get(self,request,i):
        p=Products.objects.get(id=i)
        u=request.user
        try:
            c=Cart.objects.get(user=u,product=p)# check whether the product already placed by the current user
            c.quantity += 1                       # or checks whether the products is there in the cart table
            c.save()                            # if yes increment the quanty by 1
        except Cart.DoesNotExist:
            c=Cart.objects.create(user=u,product=p,quantity=1)# else creates a new cart record inside Cart table
            return redirect('cart:cartview')

class CartView(View):
    def get(self,request,):
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.product.price*i.quantity

        context={"cart":c,'total':total}
        return render(request,"cart.html",context)
class Cartdecrement(View):
    def get(self,request,i):
        p=Products.objects.get(id=i)
        u=request.user
        try:
            c=Cart.objects.get(user=u,product=p)
            if(c.quantity>1):
             c.quantity-=1
             c.save()
            else:
              c.delete()
        except:
            pass
        return redirect('cart:cartview')
class Cartremove(View):
    def get(self, request, i):
        p = Products.objects.get(id=i)
        u = request.user
        try:
            c = Cart.objects.get(user=u, product=p)
            c.delete()
        except:
            pass
        return redirect('cart:cartview')

from cart.forms import OrderForm
def checkstock(c):
    stock=True
    for i in c:
        if i.product.stock<i.quantity:
            stock=False
            break
        else:
            stock=True
        return stock

class Checkout(View):
    def post(self,request):
        form_instance=OrderForm(request.POST)
        if form_instance.is_valid():
            o=form_instance.save(commit=False)
            u=request.user
            o.user=u
            c=Cart.objects.filter(user=u)
            total=0
            for i in c:
                total+=i.product.price*i.quantity
                o.amount=total
                o.save()
                if(o.payment_method=="online"):
                    #Razorpay client connection
                    clinet=razorpay.Client(auth=('rzp_test_ReJLO87wvNCreQ','TUpFz57IPRTE5hJQ4hr4aDzq'))
                    #place order
                    response_payment=clinet.order.create(dict(amount=total*100,currency="INR"))
                    print(response_payment)

                    id=response_payment['id']
                    o.order_id=id
                    o.save()

                    context={'payment':response_payment}
                else:
                   o.is_ordered=True
                   uid=uuid.uuid4().hex[14]
                   id="order_COD"+uid
                   o.order_id=id
                   o.save()

                for item in c:
                        order_item = Order_items.objects.create(order=o, product=item.product, quantity=item.quantity)
                        order_item.save()
                        item.product.stock -= item.quantity
                        item.product.save()
                        c.delete()

            return render(request, "paymentsucess.html")

    def get(self,request):
        u=request.user
        c=Cart.objects.filter(user=u)
        stock=checkstock(c)
        if stock:

            from_instance=OrderForm()
            context={'form':from_instance}
            return render(request,"checkout.html",context)
        else:
            messages.error(request,'cant place oder')
            return render(request,"checkout.html")
from django.contrib.auth.models import User
from django.contrib.auth import login
from cart.models import Order
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt,name="dispatch")
class PaymentSucess(View):
    def post(self,request,i):# there i respresents the username
                             # to add user into the current session again
        print(i)
        u=User.objects.get(username=i)
        login(request,u)      # adds  the user u into session

        response=request.POST
        print(response)
        id= response['razorpay_order_id']
        print(id)
        order=Order.objects.get(order_id=id)
        order.is_ordered=True
        order.save()
        # ordered item
        c=Cart.objects.filter(user=u)
        for i in c:
            o=Order_items.objects.create(order=order,product=i.product,quantity=i.quantity)
            o.save()
            o.product.stock-=o.quantity
            o.product.save()
        #cart deletion
            c.delete()

            return render(request,"paymentsucess.html")
class Orders(View):
    def get(self,request):
        u=request.user
        o=Order.objects.filter(user=u,is_ordered=True)
        context={"orders":o}
        return render(request,"orders.html",context)