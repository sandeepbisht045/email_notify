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
    
    return render(request, "index.html", {"get_data": Products.objects.all()})


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
        
            license_lst = license_date.split("-")
            expiry_lst = expiry_date.split("-")
            sdate = datetime.date(int(license_lst[0]), int(
                license_lst[1]), int(license_lst[2]))
            edate = datetime.date(int(expiry_lst[0]), int(
                expiry_lst[1]), int(expiry_lst[2]))
           
            if (edate-sdate).days >= 0 :
                Products.objects.create(name=product, sdate=sdate, edate=edate,
                                        vendor_name=vendor_name, vendor_email=vendor_email).save()
                return render(request, "index.html", {"msg": "Product has been added successfully", "get_data": Products.objects.all()})

            else:
                return render(request, "add_products.html", {"alert": "Product purchased date cannot be greater than expiry date", "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email})

    elif not request.session.get("id"):
        return render(request, "login.html", {"alert": "Login first to add products"})

    return render(request, "add_products.html")


def delete(request, id):
    if request.session.get("id"):
        if request.method == "POST":
            data = Products.objects.get(id=id)
            if data:
                data.delete()
            return redirect("/")
        else:
            return redirect("/")

    else:
        return render(request, "login.html", {"alert": "Login first to delete"})
        

def search(request):
    search = request.GET.get("search").strip().lower()
    if search:
        query=Products.objects.filter(name__icontains=search)
        if query:
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
            return render(request, "index.html", {"get_data": prods})      
        response=HttpResponse(content_type="text/csv")
        writer=csv.writer(response)
        writer.writerow(["Product Name","License Date","Expiry Date","Vendor Email","Vendor Name"])
        obj=Products.objects.all().values_list("name","sdate","edate","vendor_email","vendor_name")
        for prod in obj:
            writer.writerow(prod)
        response['Content-Disposition']='attachment;filename="Products_Details.csv"'
        return response
    
    else:
        return render(request, "login.html", {"alert": "Login first to export "})
   


# function to edit or update products
def edit_products(request,id):
    if request.method == "POST":
        print(id)
        try:
            obj=Products.objects.get(pk=id)
        except:
            return render(request, "index.html", {"msg": "Product is not available", "get_data": Products.objects.all()})

        type_=request.POST.get("type")
        if type_=="edit":
            return render(request, "edit_products.html", {"get_data": obj})
        if type_=="update":
            print(id,"update")
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
        
            license_lst = license_date.split("-")
            expiry_lst = expiry_date.split("-")
            sdate = datetime.date(int(license_lst[0]), int(
            license_lst[1]), int(license_lst[2]))
            edate = datetime.date(int(expiry_lst[0]), int(
            expiry_lst[1]), int(expiry_lst[2]))
        
        if (edate-sdate).days >= 0 :
            obj.name,obj.sdate,obj.edate,obj.vendor_name,obj.vendor_email=product, sdate,edate,vendor_name, vendor_email
            obj.save()
            return render(request, "index.html", {"msg": "Product has been updated successfully", "get_data": Products.objects.all()})
        else:
            return render(request, "edit_products.html", {"alert": "Product purchased date cannot be greater than expiry date", "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email})
  
    elif not request.session.get("id"):
        return render(request, "login.html", {"alert": "Login first to update products"})

    return render(request, "edit_products.html")

