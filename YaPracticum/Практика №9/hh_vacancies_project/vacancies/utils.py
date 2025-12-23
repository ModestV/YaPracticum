import requests
from .models import Vacancy

HH_API_BASE_URL = "https://api.hh.ru/"

def fetch_vacancies(keyword="", area=None, per_page=20):
    """
    Получает список вакансий по ключевому слову и региону.
    :param keyword: ключевое слово для поиска
    :param area: ID региона (город) — можно оставить None
    :param per_page: количество вакансий на страницу
    :return: список вакансий (словари)
    """
    url = f"{HH_API_BASE_URL}vacancies"
    params = {
        "text": keyword,
        "area": area,
        "per_page": per_page,
        "page": 0
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"Ошибка запроса: {response.status_code}")
        return []

def fetch_vacancy_detail(vacancy_id):
    """
    Получает детальную информацию о вакансии по её ID.
    :param vacancy_id: ID вакансии на HH
    :return: словарь с данными вакансии
    """
    url = f"{HH_API_BASE_URL}vacancies/{vacancy_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка запроса деталей: {response.status_code}")
        return None

def save_vacancy_from_api(vacancy_data):
    """
    Сохраняет вакансию из API в базу данных.
    :param vacancy_data: данные вакансии (словарь)
    """
    hh_id = vacancy_data["id"]
    title = vacancy_data["name"]

    employer = vacancy_data.get("employer") or {}
    company_name = employer.get("name", "")
    logo_urls = employer.get("logo_urls") or {}
    company_logo = logo_urls.get("90", "")

    area = vacancy_data.get("area") or {}
    city = area.get("name", "")

    url = vacancy_data.get("alternate_url", "")

    # Зарплата
    salary = vacancy_data.get("salary")
    salary_from = salary.get("from") if salary else None
    salary_to = salary.get("to") if salary else None

    # Категория (профессия)
    prof_roles = vacancy_data.get("professional_roles", [])
    category = prof_roles[0].get("name", "") if prof_roles else ""

    # Создаем или обновляем запись
    vacancy, created = Vacancy.objects.update_or_create(
        hh_id=hh_id,
        defaults={
            "title": title,
            "company_name": company_name,
            "company_logo": company_logo,
            "city": city,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "category": category,
            "url": url,
        }
    )

    # Если вакансия новая или нет описания — запрашиваем детали
    if created or not vacancy.description:
        detail = fetch_vacancy_detail(hh_id)
        if detail:
            description = detail.get("description", "")
            vacancy.description = description
            vacancy.save()

    return vacancy