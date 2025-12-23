"""Views для отображения динамических страниц.

Отображает страницы со списком блогов и т.д.
"""

from django.shortcuts import render

posts = [
    {
        'id': 0,
        'location': 'Деревня Веселяево',
        'date': '23 декабря 2024 года',
        'category': 'happinnes',
        'text': ''' "Трэшатина". В стрим-баре "Хата" в Екатеринбурге 
                провели проверку, по факту которой бар закрыли. 
                Стримеры проводили провокационные 
                стримы и выполняли на камеру "трэш".''',
    },
    {
        'id': 1,
        'location': 'Радон',
        'date': '29 февраля 2090 года',
        'category': 'gomer_dangerious',
        'text': '''В ИРИТ-РТФ, в кабинете СБЕРа, 
                обвалился потолок на студента группы РИ-150911. 
                Проводится проверка по факту происшествия''',
    },
    {
        'id': 2,
        'location': 'Пельменные уралы',
        'date': '13 июля 3008 года',
        'category': 'shocking',
        'text': '''Звёзды уральских пельменей сыграли свадьбу! 
                Правда, ненастоящую! В центре Екатеринбурга 
                заметили звёзд уральских пельменей!''',
    },
]


# Create your views here.
def index(request):
    """GET-запрос для отображения главной странички - списка блогов.
    :return: отображает список блогов с информацией
    """
    posts1 = posts.copy()
    posts1.reverse()
    context = {'posts': posts1}
    print(context)
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    """GET-запрос для отображения детального описания блога id и его текста.
    :param id: идентификатор блога
    :return: отображает информацию о посте
    """
    for post in posts:
        if post['id'] == id:
            context = {'real': True, 'post': post}
            return render(request, 'blog/detail.html', context)
    return render(request, 'blog/detail.html', {'real': False})


def category_posts(request, category_slug):
    """GET-запрос для вывода все блогов определённой категории.
    :param category_slug: категория блогов
    :return: (заглушка) отображает название категории
    """
    context = {'category': category_slug}
    return render(request, 'blog/category.html', context)
