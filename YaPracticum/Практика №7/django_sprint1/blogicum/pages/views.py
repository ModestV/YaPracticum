"""Views для 'статичных страниц сайта.

Содержит страницы с информацией о проекте, правилах и т.д.
"""
from django.shortcuts import render


# Create your views here.
def about(request):
    """GET-запрос для отображения странички 'О проекте'.
    :return: отображает страницу
    """
    return render(request, 'pages/about.html')


def rules(request):
    """GET-запрос для отображения странички 'Правила'.
    :return: отображает страницу
    """
    return render(request, 'pages/rules.html')
