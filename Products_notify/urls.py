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
    # ---------------------------------------certificates------------------------------------------------------------------------------
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
    path("certificate/import",views.import_certificate,name="import_certificate"),

    # ---------------------------------------domains------------------------------------------------------------------------------
    path("domains/<str:filter_>",views.domain,name="domains"),
    path("domains",views.domain,name="domains"),
    path("domain/delete/<int:id>",views.delete_domain,name="delete_domain"),
    path("domain/user/login",views.login_domain,name="login_domain"),
    path("domain/logout",views.logout_domain,name="logout_domain"),
    path("domain/search",views.search_domain,name="search_domain"),
    path("add_domain",views.add_domain,name="add_domain"),
    path("domain/export",views.export_domain,name="export_domain"),
    path("domain/edit/<int:id>/<str:param>",views.edit_domain,name="edit_domain"),
    path("mail_send_domain",views.mail_send_domain,name="mail_send_domain"),
    path("domain/subscribe",views.subscribe_domain,name="subscribe_domain"),
    path("domain/import",views.import_domain,name="import_domain"),








]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
