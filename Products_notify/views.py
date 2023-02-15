from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products, User,Subscribe,Certificates
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
                    prod_lst.append(f"{i.name} will expire today")
            elif difference<0:
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


def tabular(request,filter_=None):
    
    get_data = Products.objects.all()
    filter_selected=""
    if filter_:
        if filter_=="latest":
            get_data = Products.objects.all().order_by('-id')
        elif filter_=="earliest":
            get_data = Products.objects.all()
        elif filter_=="expired":
            get_data = Products.objects.filter(expires_in__lt=0)
        elif filter_=="active":
            get_data = Products.objects.filter(expires_in__gte=0)
        filter_selected=filter_
    if get_data:
        for i in get_data:
            difference = (i.edate-cur_date).days
            i.expires_in=difference
            i.save()       
    
    return render(request, "index.html", {"get_data": get_data,"filter_selected":filter_selected})



def login(request):
    info=""
    if not request.session.get("id"):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            filter_data = User.objects.filter(email=email, password=password).first()
            if filter_data:
                request.session["id"] = filter_data.id
                return redirect("/tabular")
            else:
                info="Invalid email or password"
                return render(request, "index.html", {"open_edit_modal":"invalid_cred","alert":"invalid","info": info,"email":email,"get_data":Products.objects.all()})
        return redirect("/tabular")
    return redirect("/tabular")


def logout(request):
    if request.session.get("id"):
        request.session.clear()
        return redirect("/tabular")


def add_products(request):
    if not request.session.get("id"):
        info="Please login first to add products"
        return render(request, "index.html", {"alert": "login_first","info":info,"get_data":Products.objects.all()})
    if request.method == "POST":
            info=''
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            payment_mode=request.POST.get("payment_mode")
            
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
           
            if(sdate-cur_date).days > 0:
                info='Product purchased date cannot be greater than current date'
                return render(request, "index.html", {"alert": "pd_g_cd","open_modal":"open_modal","info":info, "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email,"sdate":sdate,"edate":edate,"get_data": Products.objects.all()})
            elif(edate-sdate).days < 0:
                info='Product purchased date cannot be greater than expiry date'
                return render(request, "index.html", {"alert": "pd_g_ed","open_modal":"open_modal","info":info, "product": product, "vendor_name": vendor_name, "vendor_email": vendor_email,"sdate":sdate,"edate":edate,"get_data": Products.objects.all()})
            else:
                expires_in = (edate-cur_date).days
                Products.objects.create(name=product, sdate=sdate, edate=edate,payment_mode=payment_mode,
                                        vendor_name=vendor_name, vendor_email=vendor_email,expires_in=expires_in).save()
                info='Product has been added successfully'
                return render(request, "index.html", {"alert": "added_success","info":info, "get_data": Products.objects.all()})

    return render(request, "index.html",{"get_data":Products.objects.all()})


def delete(request,id):
    if request.session.get("id"):
        try:
            data = Products.objects.get(id=id)
            data.delete()
            return redirect("/tabular")

        except:
            return redirect("/tabular")
        
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
             return redirect("/tabular")

    else:
        return redirect("/tabular")



def subscribe(request):
    info=""
    if request.session.get("id"):
        if request.method=="POST":
            email = request.POST.get("email")
            
            subs=Subscribe.objects.filter(email=email).first()
            if subs:
                status=subs.status
                if status==1:
                    subs.status=0
                    subs.save()
                    info= "You have unsubscribed & won't get any alert regarding products expiry in future"
                    return render(request, "index.html", {"info":info,"alert":"unsubscribed", "get_data": Products.objects.all()})

                else:
                    subs.status=1
                    subs.save()
                    info= "You have subscribed successfully for email alert"
                    return render(request, "index.html", {"info":info, "get_data": Products.objects.all(),"alert":"subscribed"})
        
            else:
                Subscribe.objects.create(email=email).save()
                info= "You have subscribed successfully for email alert"
                return render(request, "index.html", {"info":info, "get_data": Products.objects.all(),"alert":"subscribed"})

        else:
            return redirect("/tabular")
    else:
        info="Login first to continue"
        return render(request, "index.html", {"alert": "login_first ","info":info,"get_data": Products.objects.all()})
        

def export(request):
    info=""
    if request.session.get("id"):
        prods=Products.objects.all()
        if not prods:
            return redirect("/tabular")     
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
        info="Loin first to continue"
        return render(request, "index.html", {"alert": "login_first ","info":info,"get_data":prods})
   


# function to edit or update products
def edit_products(request,id,param):
    info=''
    if not request.session.get("id"):
        info="Please login first to add products"
        return render(request, "index.html", {"alert": "login_first","info":info})
    try:
        obj=Products.objects.get(pk=id)
    except:
        info='Products are not available'
        return render(request, "index.html", {"info":info,"alert":"not_available", "get_data": Products.objects.all()})
    if request.method == "GET":

        if param == "edit":
            return render(request, "index.html", {"id":obj.id,"product":obj.name, "vendor_name": obj.vendor_name, 
            "vendor_email": obj.vendor_email,"sdate":obj.sdate,"edate":obj.edate,"payment_mode":obj.payment_mode,"c":"Credit Card"
            ,"p":"Purchase Order","a":"Agreement","param":"edit","get_data":Products.objects.all()})
        else:
            return redirect("/tabular")
    if request.method=='POST':
        if param=="update":
            product = request.POST.get("product")
            vendor_name = request.POST.get("vendor_name")
            vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            payment_mode=request.POST.get("payment_mode")
        
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
            dict_data={"open_edit_modal":"open_edit_modal","c":"Credit Card"
                ,"p":"Purchase Order","a":"Agreement","id":obj.id,"product":product, "vendor_name":vendor_name,
                "vendor_email":vendor_email,"sdate":sdate,"edate":edate,"payment_mode":payment_mode,
                "get_data": Products.objects.all()}
            if (sdate-cur_date).days > 0:
                info="Product purchased date cannot be greater than current date"
                dict_data.update({"alert": "pd_g_cd","info":info})
                return render(request, "index.html", dict_data)
            elif(edate-sdate).days < 0:
                info="Product purchased date cannot be greater than expiry date"
                dict_data.update({"alert": "pd_g_ed","info":info})
                return render(request, "index.html", dict_data)
    
            else:
                difference = (edate-cur_date).days
                obj.name,obj.sdate,obj.edate,obj.vendor_name,obj.vendor_email,obj.payment_mode,obj.expires_in=product, sdate,edate,vendor_name, vendor_email,payment_mode,difference
                obj.save()

                info="Product has been updated successfully"
                return render(request, "index.html", {"alert":"updated_success","info": info, "get_data": Products.objects.all()})
        else:
            return render(request,"index.html",{"get_data":Products.objects.all()})

    # return render(request, "edit_products.html")


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
                
            return redirect("/tabular")
        return redirect("/tabular")
    except:
        return redirect("/tabular")


def tabs(request):
    return render(request,"sample.html")
    # ----------------------------------------------------------------------------------------------------

def certificates(request,filter_=None):
    get_data = Certificates.objects.all()
    filter_selected=""
    if filter_:
        # if filter_=="latest":
        #     get_data = Certificates.objects.all().order_by('-id')
        # elif filter_=="earliest":
        #     get_data = Certificates.objects.all()
        if filter_=="expired":
            get_data = Certificates.objects.filter(expires_in__lt=0)
        elif filter_=="active":
            get_data = Certificates.objects.filter(expires_in__gte=0)
        filter_selected=filter_
    if get_data:
        for i in get_data:
            difference = (i.edate-cur_date).days
            i.expires_in=difference
            i.save()       
    
    return render(request, "certificate.html", {"get_data": get_data,"filter_selected":filter_selected})

def delete_certificate(request,id):
    if request.session.get("id"):
        try:
            data = Certificates.objects.get(id=id)
            data.delete()
            return redirect("/certificates")

        except:
            return redirect("/certificates")
        
    else:
        return render(request, "login.html", {"alert": "Login first to delete"})

def login_certificate(request):
    info=""
    if not request.session.get("id"):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            filter_data = User.objects.filter(email=email, password=password).first()
            if filter_data:
                request.session["id"] = filter_data.id
                return redirect("/certificates")
            else:
                info="Invalid email or password"
                return render(request, "index.html", {"open_edit_modal":"invalid_cred","alert":"invalid","info": info,"email":email,"get_data":Certificates.objects.all()})
        return redirect("/certificates")
    return redirect("/certificates")

def logout_certificate(request):
    if request.session.get("id"):
        request.session.clear()
        return redirect("/certificate")
    return redirect("/certificates")

def search_certificate(request):
    search = request.GET.get("search").strip().lower()
    if search:
        query=Certificates.objects.filter(name__icontains=search)
        if query:
            for i in query:
                difference = (i.edate-cur_date).days
                i.expires_in=difference
                i.save()       
            return render(request,"certificate.html",{"get_data":query})
        else:
             return redirect("/certificates")

def add_certificate(request):
    if not request.session.get("id"):
        info="Please login first to add certificate"
        return render(request, "index.html", {"alert": "login_first","info":info,"get_data":Certificates.objects.all()})
    if request.method == "POST":
            info=''
            product = request.POST.get("product")
            # vendor_name = request.POST.get("vendor_name")
            # vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            auto_renew=request.POST.get("auto_renew")
            auto_renew= 0 if auto_renew=='off' else 1
            price=request.POST.get("price")

            
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
           
            if(sdate-cur_date).days > 0:
                info='Certificate purchased date cannot be greater than current date'
                return render(request, "certificate.html", {"alert": "pd_g_cd","open_modal":"open_modal","info":info, "product": product,"price":price, "sdate":sdate,"edate":edate,"get_data": Certificates.objects.all()})
            elif(edate-sdate).days < 0:
                info='Certificate purchased date cannot be greater than expiry date'
                return render(request, "certificate.html", {"alert": "pd_g_ed","open_modal":"open_modal","info":info, "product": product,"price":price, "sdate":sdate,"edate":edate,"get_data": Certificates.objects.all()})
            else:
                expires_in = (edate-cur_date).days
                Certificates.objects.create(name=product, sdate=sdate, edate=edate,price=price,auto_renew=auto_renew,
                                        expires_in=expires_in).save()
                info='Certificate has been added successfully'
                return render(request, "certificate.html", {"alert": "added_success","info":info, "get_data": Certificates.objects.all()})

    return render(request, "certificate.html",{"get_data":Certificates.objects.all()})


def export_certificate(request):
    info=""
    if request.session.get("id"):
        prods=Certificates.objects.all()
        if not prods:
            return redirect("/certificates")     
        for i in prods:
            difference = (i.edate-cur_date).days
            i.expires_in=difference
            i.save()   
        response=HttpResponse(content_type="text/csv")
        writer=csv.writer(response)
        writer.writerow(["Certificate Name","License Date","Expiry Date","Auto_Renew","Price","Status"])
        obj=Certificates.objects.all().values_list("name","sdate","edate","auto_renew","price","expires_in")
        for prod in obj:
            prod=list(prod)
            sdate=prod[len(prod)-5]
            edate=prod[len(prod)-4]
            auto_renew=prod[len(prod)-3]
            prod[len(prod)-3]= 'on' if prod[len(prod)-3]==1 else 'off'
            
            prod[len(prod)-5]=f"{sdate.day}-{sdate.month}-{sdate.year}"
            prod[len(prod)-4]=f"{edate.day}-{edate.month}-{edate.year}"
            if int(prod[len(prod)-1])<0:
                prod[len(prod)-1]="Expired"
            else:
                prod[len(prod)-1]="Active"
            writer.writerow(prod)
        response['Content-Disposition']='attachment;filename="Certificate_Details.csv"'
        return response
    else:
        info="Loin first to continue"
        return render(request, "certificate.html", {"alert": "login_first ","info":info,"get_data":prods})
   
def edit_certificate(request,id,param):
    info=''
    if not request.session.get("id"):
        info="Please login first to add certificate"
        return render(request, "certificate.html", {"alert": "login_first","info":info})
    try:
        obj=Certificates.objects.get(pk=id)
    except:
        info='Certificates are not available'
        return render(request, "certificate.html", {"info":info,"alert":"not_available", "get_data": Certificates.objects.all()})
    if request.method == "GET":

        if param == "edit":
            obj.auto_renew= 'off' if obj.auto_renew==0 else 'on'

            return render(request, "certificate.html", {"id":obj.id,"product":obj.name,  
            "sdate":obj.sdate,"edate":obj.edate,"auto_renew":obj.auto_renew,"on":"On",'price':obj.price
            ,"off":"off","param":"edit","get_data":Certificates.objects.all()})
        else:
            return redirect("/certificate")
    if request.method=='POST':
        if param=="update":
            product = request.POST.get("product")
            # vendor_name = request.POST.get("vendor_name")
            # vendor_email = request.POST.get("vendor_email")
            license_date = request.POST.get("license_date")
            expiry_date = request.POST.get("expiry_date")
            price=request.POST.get("price")
            auto_renew=request.POST.get("auto_renew")

        
            sdate=datetime.datetime.strptime(license_date,'%Y-%m-%d').date()
            edate=datetime.datetime.strptime(expiry_date,'%Y-%m-%d').date()
            dict_data={"open_edit_modal":"open_edit_modal","off":"Off"
                ,"on":"On","id":obj.id,"product":product, 
               "sdate":sdate,"edate":edate,"price":price,auto_renew:auto_renew,
                "get_data": Certificates.objects.all()}
            if (sdate-cur_date).days > 0:
                info="Certificate purchased date cannot be greater than current date"
                dict_data.update({"alert": "pd_g_cd","info":info})
                return render(request, "certificate.html", dict_data)
            elif(edate-sdate).days < 0:
                info="Certificate purchased date cannot be greater than expiry date"
                dict_data.update({"alert": "pd_g_ed","info":info})
                return render(request, "certificate.html", dict_data)
    
            else:
                auto_renew= 0 if auto_renew=='off' else 1
                difference = (edate-cur_date).days
                obj.name,obj.sdate,obj.edate,obj.auto_renew,obj.price,obj.expires_in=product, sdate,edate,auto_renew,price,difference
                obj.save()
                info="Certificate has been updated successfully"
                return render(request, "certificate.html", {"alert":"updated_success","info": info, "get_data": Certificates.objects.all()})
        else:
            return render(request,"certificate.html",{"get_data":Certificates.objects.all()})

def mail_send_certificate(request):
    prod_lst = []
    get_data = Certificates.objects.all()
    if get_data:
        for i in get_data:
            difference = (i.edate-cur_date).days
            if difference <= 30 and difference > 0:
           #     if difference%5==0 or difference==1:
                  prod_lst.append(f"{i.name} : {difference} days")
            #    elif difference==0:
            elif difference==0:
                    prod_lst.append(f"{i.name} will expire today")
            elif difference<0:
                    prod_lst.append(f"{i.name} expired")
        if prod_lst:
            htmlgen = f"<h3> Your purchased certificates will expire as mentioned below : </h3> <br>"
            for i in prod_lst:
                htmlgen += f"<ul><list><b> {i}</b></list> </ul><br>"
            lst=[]
            emails=Subscribe.objects.filter(status=1)
            if not emails:
                return HttpResponse("no emails subscribed")
            for i in emails:
                lst.append(i.email)

            send_mail('Certificates Expiry Alert', "", 'scan@freecharge.com',
                      lst, fail_silently=False, html_message=htmlgen)

            return HttpResponse("success")
        else:
            return HttpResponse("failed")
    else:
        return HttpResponse("Certificates are not available in the db")

def subscribe_certificate(request):
    info=""
    if request.session.get("id"):
        if request.method=="POST":
            email = request.POST.get("email")
            
            subs=Subscribe.objects.filter(email=email).first()
            if subs:
                status=subs.status
                if status==1:
                    subs.status=0
                    subs.save()
                    info= "You have unsubscribed & won't get any alert regarding certificates expiry in future"
                    return render(request, "certificate.html", {"info":info,"alert":"unsubscribed", "get_data": Certificates.objects.all()})

                else:
                    subs.status=1
                    subs.save()
                    info= "You have subscribed successfully for email alert"
                    return render(request, "certificate.html", {"info":info, "get_data": Certificates.objects.all(),"alert":"subscribed"})
        
            else:
                Subscribe.objects.create(email=email).save()
                info= "You have subscribed successfully for email alert"
                return render(request, "certificate.html", {"info":info, "get_data": Certificates.objects.all(),"alert":"subscribed"})

        else:
            return redirect("/certificates")
    else:
        info="Login first to continue"
        return render(request, "certificate.html", {"alert": "login_first ","info":info,"get_data": Certificates.objects.all()})
        