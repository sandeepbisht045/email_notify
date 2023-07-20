from django.db import models

# Create your models here.
class Products(models.Model):
    name=models.CharField(max_length=50)
    sdate=models.DateField(default="2022-01-01")
    edate=models.DateField(default="2022-01-01")
    photo=models.ImageField(upload_to="",default="default.png")
    expires_in=models.IntegerField(default=0)
    vendor_email=models.EmailField(default="",max_length=50)
    vendor_name=models.CharField(max_length=50)
    payment_mode=models.CharField(max_length=50,default="")


    def __str__(self):
        return self.name

class Certificates(models.Model):
    name=models.CharField(max_length=50)
    sdate=models.DateField()
    edate=models.DateField()
    expires_in=models.IntegerField(default=0)
    price=models.IntegerField(default=0)
    auto_renew=models.IntegerField(default=0)
    # photo=models.ImageField(upload_to="",default="default.png")
    # vendor_email=models.EmailField(default="",max_length=50)
    # vendor_name=models.CharField(max_length=50)
    # payment_mode=models.CharField(max_length=50,default="")

    def __str__(self):
        return self.name


class User(models.Model):
    email=models.EmailField(default="",max_length=50)
    password=models.CharField(max_length=50)

    def __str__(self):
        return self.email

class Subscribe(models.Model):
    email=models.EmailField(default="",max_length=50)
    status=models.IntegerField(default=1)
    def __str__(self):
        return self.email