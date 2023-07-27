from django.contrib import admin
from .models import Products,User,Subscribe,Certificates,Domains
# Register your models here.
admin.site.register(Products)
admin.site.register(User)
admin.site.register(Subscribe)
admin.site.register(Certificates)
admin.site.register(Domains)


