"""URL Configuration for LawGenius project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LawGenius.mainapp.urls')),
]