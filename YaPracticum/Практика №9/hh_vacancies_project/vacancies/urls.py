from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    path('', views.vacancy_catalog, name='catalog'),
    path('search/', views.vacancy_search, name='search'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='detail'),
]