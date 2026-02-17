from django.contrib import admin
from django.urls import path, include
from .views import checkout_booking

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]