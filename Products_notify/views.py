from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products, User,Subscribe
import datetime,csv,os
from django.core.mail import send_mail
import pandas as pd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from Ajay_Portal.settings import BASE_DIR
# Create your views here.

cur_time = datetime.datetime.now()
cur_date=cur_time.date()

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


def index(request,param=None):
    msg,pr_="",""
    get_data = Products.objects.all()
    if param!=None:
        return render(request,"index.html",{"show_modal":"modal","get_data":get_data})

    param_=request.GET.get("res")
    filter_=request.GET.get("filter")
    if filter_:
        if filter_=="latest":
            get_data = Products.objects.all().order_by('-id')
        elif filter_=="earliest":
            get_data = Products.objects.all()
        elif filter_=="expired":
            get_data = Products.objects.filter(expires_in__lt=0)
        elif filter_=="active":
            get_data = Products.objects.filter(expires_in__gte=0)
        
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
            # if difference <= 30 and difference > 0:
            i.expires_in=difference
            i.save()       
           
    return render(request, "index.html", {"get_data": get_data,"msg":msg,"param":pr_})


def login(request):
    if not request.session.get("id"):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            filter_data = User.objects.filter(email=email, password=password).first()
            if filter_data:
                request.session["id"] = filter_data.id

                return redirect("/")
            else:
                return render(request, "login.html", {"alert": "Invalid email or password","email":email})

    return render(request, "login.html")


def logout(request):
    if request.session.get("id"):
        request.session.clear()
        return redirect("/login")


def add_products(request):
    if request.method == "POST":
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            payment_mode=request.POST.get("payment_mode")
            
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
            # license_lst = license_date.split("-")
            # expiry_lst = expiry_date.split("-")
            # sdate = datetime.date(int(license_lst[0]), int(
            #     license_lst[1]), int(license_lst[2]))
            # edate = datetime.date(int(expiry_lst[0]), int(
            #     expiry_lst[1]), int(expiry_lst[2]))
           
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
                i.expires_in=difference
                i.save()       
            return render(request,"index.html",{"get_data":query})
        else:
             return redirect("/")

    else:
        return redirect("/")



def subscribe(request):
    if request.session.get("id"):
        email = request.GET.get("email")
        
        subs=Subscribe.objects.filter(email=email).first()
        if subs:
            status=subs.status
            if status==1:
                subs.status=0
                subs.save()
                return render(request, "index.html", {"msg": "You have unsubscribed & won't get any alert regarding products expiry in future", "get_data": Products.objects.all()})

            else:
                # subs.update(status=1)
                subs.status=1
                subs.save()
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
        for i in prods:
            difference = (i.edate-cur_date).days
            i.expires_in=difference
            i.save()   
        response=HttpResponse(content_type="text/csv")
        writer=csv.writer(response)
        writer.writerow(["Product Name","License Date","Expiry Date","Vendor Email","Vendor Name","Payment Mode","Status"])
        obj=Products.objects.all().values_list("name","sdate","edate","vendor_email","vendor_name","payment_mode","expires_in")
        for prod in obj:
            prod=list(prod)
            sdate=prod[len(prod)-6]
            edate=prod[len(prod)-5]
            
            prod[len(prod)-6]=f"{sdate.day}-{sdate.month}-{sdate.year}"
            prod[len(prod)-5]=f"{edate.day}-{edate.month}-{edate.year}"
            if int(prod[len(prod)-1])<0:
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
        
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
                 
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


def import_file(request):
    try:
        if request.method == 'POST' and request.FILES['import']:
          
            imported_file = request.FILES['import']        
            fs = FileSystemStorage()
            csv_file = fs.save(imported_file.name, imported_file)
            uploaded_file_url = fs.url(csv_file)
            # name, extension = os.path.splitext(uploaded_file_url)
            
            excel_file = uploaded_file_url
            print(excel_file)
            file_data = pd.read_csv("."+excel_file,encoding='utf-8')
           
            dbframe = file_data
            os.remove(f"{BASE_DIR}/{uploaded_file_url}")
            payment_type=('Credit Card',"Agreement","Purchase Order")
            for dbframe in dbframe.itertuples():
                license_date=datetime.datetime.strptime(dbframe.License, '%d-%m-%Y').date()
                expiry_date=datetime.datetime.strptime(dbframe.Expiry, '%d-%m-%Y').date()
                
                if license_date and expiry_date:
                    if (license_date-cur_date).days > 0 or (expiry_date-license_date).days < 0 or (dbframe.Payment not in payment_type):
                        continue
                    new_obj=Products.objects.create(name=dbframe.ProductName,sdate=license_date,edate=expiry_date
                    ,vendor_email=dbframe.VendorEmail,vendor_name=dbframe.VendorName,payment_mode=dbframe.Payment)
                    new_obj.save()
                
            return redirect("/")
        return redirect("/")
    except:
        return redirect("/")

