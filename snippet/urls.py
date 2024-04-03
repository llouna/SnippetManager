from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("gestion.urls")),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('accounts/', include('allauth.urls')),
    path("admin/", admin.site.urls),
]