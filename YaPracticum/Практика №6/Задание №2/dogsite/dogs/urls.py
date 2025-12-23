from django.urls import path
from . import views

urlpatterns = [
    path('', views.dogs_list_view, name='dogs_list'),
    path('images/', views.dogs_images_view, name='dogs_images'),
]