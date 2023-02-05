from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
urlpatterns = [
    path("login",views.login,name="login"),
    path("add_products",views.add_products,name="add_products"),
    path("logout",views.logout,name="logout"),
    path("mail_send",views.mail_send,name="mail_send"),
    path("delete/<int:id>",views.delete,name="delete"),
    path("search",views.search,name="search"),
    path("subscribe",views.subscribe,name="subscribe"),
    path("export",views.export,name="export"),
    path("import",views.import_file,name="import"),
    path("tabular",views.tabular,name="tabular"),
    path("tabular/<str:filter_>",views.tabular,name="tabular_filter"),
    path("edit/<int:id>/<str:param>",views.edit_products,name="edit_products"),
    path("",views.tabs,name="tabs"),
    # ---------------------------------------------------------------------------------------------------------------------
    path("certificates/<str:filter_>",views.certificates,name="certificates"),
    path("certificates",views.certificates,name="certificates"),
    path("certificates/delete/<int:id>",views.delete_certificate,name="delete_certificate"),
    path("certificate/login",views.login_certificate,name="login_certificate"),
    path("certificate/logout",views.logout_certificate,name="logout_certificate"),
    path("certificate/search",views.search_certificate,name="search_certificate"),
    path("add_certificate",views.add_certificate,name="add_certificate"),
    path("certificate/export",views.export_certificate,name="export_certificate"),
    path("certificate/edit/<int:id>/<str:param>",views.edit_certificate,name="edit_certificate"),
    path("mail_send_certificate",views.mail_send_certificate,name="mail_send_certificate"),
    path("certificate/subscribe",views.subscribe_certificate,name="subscribe_certificate"),







]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
