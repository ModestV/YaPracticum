"""Настройка админ-панели. Регистрация моделей."""
# Register your models here.
from django.contrib import admin

# Из модуля models импортируем модель Category...
from .models import Category, Location, Post

# ...и регистрируем её в админке:
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
