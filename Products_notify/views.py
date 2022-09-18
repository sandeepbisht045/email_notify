from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products, User,Subscribe
import datetime,csv
from django.core.mail import send_mail
# Create your views here.

x = datetime.datetime.now()
day = x.strftime("%d")
month = x.strftime("%m")
year = x.strftime("%Y")
cur_date = datetime.date(int(year), int(month), int(day))

def mail_send(request):
    prod_lst = []
    get_data = Products.objects.all()
    if get_data:
        for i in get_data:
            difference = (i.edate-cur_date).days
            if difference <= 30 and difference > 0:
           #     if difference%5==0 or difference==1:
                  prod_lst.append(f"{i.name} : {difference} days")
            #    elif difference==0:
            elif difference==0:
                    prod_lst.append(f"{i.name} expired")
        if prod_lst:
            htmlgen = f"<h3> Your purchased products will expire as mentioned below : </h3> <br>"
            for i in prod_lst:
                htmlgen += f"<ul><list><b> {i}</b></list> </ul><br>"
            lst=[]
            emails=Subscribe.objects.filter(status=1)
            if not emails:
                return HttpResponse("no emails subscribed")
            for i in emails:
                lst.append(i.email)

            send_mail('Products Expiry Alert', "", 'scan@freecharge.com',
                      lst, fail_silently=False, html_message=htmlgen)

            return HttpResponse("success")
        else:
            return HttpResponse("failed")
    else:
        return HttpResponse("Products are not available in the db")


def index(request):
    msg,pr_="",""
    get_data = Products.objects.all()
    param_=request.GET.get("res")
    if param_:
        pr_="param"
        if param_=="updated":
            msg="Product has been updated successfully"
        elif param_=="added":
            msg="Product has been added successfully"
        elif param_=="unsubscribe":
            msg="You have unsubscribed & won't get any alert regarding products expiry in future"
        elif param_=="subscribe":
            msg="You have subscribed successfully for email alert"
        elif param_=="not_available":
            msg="Product is not available"
    if get_data:
        for i in get_data:
            difference = (i.edate-cur_date).days
            if difference <= 30 and difference > 0:
                i.expires_in=difference
                i.save()       
            elif difference<0:
                i.expires_in=difference
                i.save()
            elif difference==0:
                i.expires_in=0
                i.save()
                                     
    return render(request, "index.html", {"get_data": get_data,"msg":msg,"param":pr_})


def login(request):
    if not request.session.get("id"):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            

            filter_data = User.objects.filter(email=email, password=password)
            if filter_data.exists():
                for i in filter_data:
                    request.session["id"] = i.id

                return redirect("/")
            else:
                return render(request, "login.html", {"alert": "Invalid email or password","email":email})

    return render(request, "login.html")


def logout(request):
    if request.session.get("id"):
        request.session.clear()
        return redirect("/")


def add_products(request):
    if request.method == "POST":
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            payment_mode=request.POST.get("payment_mode")
            
        
            license_lst = license_date.split("-")
            expiry_lst = expiry_date.split("-")
            sdate = datetime.date(int(license_lst[0]), int(
                license_lst[1]), int(license_lst[2]))
            edate = datetime.date(int(expiry_lst[0]), int(
                expiry_lst[1]), int(expiry_lst[2]))
           
            if(sdate-cur_date).days > 0:
                return render(request, "add_products.html", {"alert": "Product purchased date cannot be greater than current date", "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email,"sdate":sdate,"edate":edate})
            elif(edate-sdate).days < 0:
                return render(request, "add_products.html", {"alert": "Product purchased date cannot be greater than expiry date", "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email,"sdate":sdate,"edate":edate})
            else:
                expires_in = (edate-cur_date).days
                Products.objects.create(name=product, sdate=sdate, edate=edate,payment_mode=payment_mode,
                                        vendor_name=vendor_name, vendor_email=vendor_email,expires_in=expires_in).save()
                return render(request, "index.html", {"msg": "Product has been added successfully", "get_data": Products.objects.all()})


    elif not request.session.get("id"):
        return render(request, "login.html", {"alert": "Login first to add products"})

    return render(request, "add_products.html")


def delete(request,id):
    if request.session.get("id"):
        try:
            data = Products.objects.get(id=id)
            data.delete()
            return redirect("/")

        except:
            return redirect("/")
        
    else:
        return render(request, "login.html", {"alert": "Login first to delete"})
        

def search(request):
    search = request.GET.get("search").strip().lower()
    if search:
        query=Products.objects.filter(name__icontains=search)
        if query:
            for i in query:
                difference = (i.edate-cur_date).days
                if difference <= 30 and difference > 0:
                    i.expires_in=difference
                    i.save()       
                elif difference<=0:
                    i.expires_in=0
                    i.save()
            return render(request,"index.html",{"get_data":query})
        else:
             return redirect("/")

    else:
        return redirect("/")



def subscribe(request):
    if request.session.get("id"):
        email = request.GET.get("email")
        
        subs=Subscribe.objects.filter(email=email)
        if subs:
            for i in subs:
                status=i.status
            if status==1:
                subs.update(status=0)
                return render(request, "index.html", {"msg": "You have unsubscribed & won't get any alert regarding products expiry in future", "get_data": Products.objects.all()})

            else:
                subs.update(status=1)
                return render(request, "index.html", {"msg": "You have subscribed successfully for email alert", "get_data": Products.objects.all()})
    
        else:
            Subscribe.objects.create(email=email).save()
            return render(request, "index.html", {"msg": "You have subscribed successfully for email alert", "get_data": Products.objects.all()})

           
    else:
        return render(request, "login.html", {"alert": "Login first to proceed"})
        

def export(request):
    if request.session.get("id"):
        prods=Products.objects.all()
        if not prods:
            return redirect("/")     
        response=HttpResponse(content_type="text/csv")
        writer=csv.writer(response)
        writer.writerow(["Product Name","License Date","Expiry Date","Vendor Email","Vendor Name","Payment Mode","Status"])
        obj=Products.objects.all().values_list("name","sdate","edate","vendor_email","vendor_name","payment_mode","expires_in")
        for prod in obj:
            prod=list(prod)
            if prod[len(prod)-1]==0:
                prod[len(prod)-1]="Expired"
            else:
                prod[len(prod)-1]="Active"
            writer.writerow(prod)
        response['Content-Disposition']='attachment;filename="Products_Details.csv"'
        return response
    else:
        return render(request, "login.html", {"alert": "Login first to export "})
   


# function to edit or update products
def edit_products(request,id):
    if request.method == "POST":
        
        try:
            obj=Products.objects.get(pk=id)
            print("obj",id)
        except:
            return render(request, "index.html", {"msg": "Product is not available", "get_data": Products.objects.all()})

        type_=request.POST.get("type")
        if type_=="edit":
            return render(request, "edit_products.html", {"get_data": obj,"c":"Credit Card"
            ,"p":"Purchase Order","a":"Agreement"})
        if type_=="update":
            
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            payment_mode=request.POST.get("payment_mode")
        
            license_lst = license_date.split("-")
            expiry_lst = expiry_date.split("-")
            sdate = datetime.date(int(license_lst[0]), int(
            license_lst[1]), int(license_lst[2]))
            edate = datetime.date(int(expiry_lst[0]), int(
            expiry_lst[1]), int(expiry_lst[2]))
        
        if (sdate-cur_date).days > 0:
                return render(request, "edit_products.html", {"alert": "Product purchased date cannot be greater than current date","get_data": obj,"c":"Credit Card"
            ,"p":"Purchase Order","a":"Agreement"})
        elif(edate-sdate).days < 0:
            return render(request, "edit_products.html", {"alert": "Product purchased date cannot be greater than expiry date","get_data": obj,"c":"Credit Card"
            ,"p":"Purchase Order","a":"Agreement"})
  
        else:
            obj.name,obj.sdate,obj.edate,obj.vendor_name,obj.vendor_email,obj.payment_mode=product, sdate,edate,vendor_name, vendor_email,payment_mode
            obj.save()
            return render(request, "index.html", {"msg": "Product has been updated successfully", "get_data": Products.objects.all()})
        

    elif not request.session.get("id"):
        return render(request, "login.html", {"alert": "Login first to update products"})

    return render(request, "edit_products.html")

