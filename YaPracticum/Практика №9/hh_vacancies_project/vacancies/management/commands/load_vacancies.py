from django.core.management.base import BaseCommand
from vacancies.utils import fetch_vacancies, save_vacancy_from_api

class Command(BaseCommand):
    help = 'Загружает вакансии с HH API'

    def add_arguments(self, parser):
        parser.add_argument('--keyword', type=str, default='', help='Ключевое слово для поиска')
        parser.add_argument('--area', type=int, default=None, help='ID региона (города)')
        parser.add_argument('--count', type=int, default=20, help='Количество вакансий')

    def handle(self, *args, **options):
        keyword = options['keyword']
        area = options['area']
        count = options['count']

        self.stdout.write(f"Загрузка вакансий по запросу '{keyword}'...")
        vacancies_list = fetch_vacancies(keyword=keyword, area=area, per_page=count)

        for item in vacancies_list:
            vacancy = save_vacancy_from_api(item)
            self.stdout.write(f"✅ {vacancy.title} ({vacancy.company_name})")

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(vacancies_list)} вакансий.'))