from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

r = DefaultRouter()

urlpatterns = [
    path('', include(r.urls))
]