"""Views для отображения динамических страниц.

Отображает страницы со списком блогов и т.д.
"""

from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.http import Http404
import datetime

from .models import Post, Category

posts = []


# Create your views here.
def index(request):
    """GET-запрос для отображения главной странички - списка блогов.
    :return: отображает список блогов с информацией
    """
    posts = (
        Post.objects
        .select_related('category')
        .filter(pub_date__lt=datetime.datetime.now())
        .filter(is_published=True)
        .filter(category__is_published=True)
        .order_by('-pub_date')
    )[0:5]
    context = {'post_list': posts}
    print(context)
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    """GET-запрос для отображения детального описания блога id и его текста.
    :param id: идентификатор блога
    :return: отображает информацию о посте
    """
    post = get_object_or_404(
        Post.objects
        .select_related('category')
        .filter(
            Q(pub_date__lt=datetime.datetime.now())
            & Q(is_published=True)
            & Q(category__is_published=True)
        ),
        id=id
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """GET-запрос для вывода всех блогов определённой категории.
    :param category_slug: категория блогов
    :return: отображает посты из категории
    """
    category = Category.objects.get(slug=category_slug)
    if not category.is_published:
        raise Http404('Такого блога не существует.')
    category_posts = (
        Post.objects
        .select_related('category')
        .filter(category__slug=category_slug)
        .filter(is_published=True)
        .filter(pub_date__lt=datetime.datetime.now())
    )
    context = {'post_list': category_posts, 'category': category}
    return render(request, 'blog/category.html', context)
