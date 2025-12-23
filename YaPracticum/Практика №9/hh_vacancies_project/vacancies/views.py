from django.shortcuts import render, get_object_or_404
from .models import Vacancy
from .utils import fetch_vacancies, save_vacancy_from_api

def vacancy_catalog(request):
    """Каталог всех вакансий"""
    vacancies = Vacancy.objects.all().order_by('-id')  # последние сверху
    context = {
        'vacancies': vacancies,
    }
    return render(request, 'vacancies/catalog.html', context)

def vacancy_search(request):
    """Поиск и фильтрация вакансий"""
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    category = request.GET.get('category', '')

    vacancies = Vacancy.objects.all()

    if query:
        vacancies = vacancies.filter(title__icontains=query)
    if city:
        vacancies = vacancies.filter(city__icontains=city)
    if category:
        vacancies = vacancies.filter(category__icontains=category)

    context = {
        'vacancies': vacancies,
        'query': query,
        'city': city,
        'category': category,
    }
    return render(request, 'vacancies/search.html', context)

def vacancy_detail(request, vacancy_id):
    """Детальная страница вакансии"""
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
    context = {
        'vacancy': vacancy,
    }
    return render(request, 'vacancies/detail.html', context)