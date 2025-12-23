from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=500, verbose_name="Название")
    company_name = models.CharField(max_length=300, verbose_name="Название компании", blank=True, null=True)
    company_logo = models.URLField(max_length=500, verbose_name="Логотип компании", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    salary_from = models.IntegerField(verbose_name="Зарплата от", blank=True, null=True)
    salary_to = models.IntegerField(verbose_name="Зарплата до", blank=True, null=True)
    category = models.CharField(max_length=200, verbose_name="Категория профессии", blank=True, null=True)
    hh_id = models.CharField(max_length=50, unique=True, verbose_name="ID вакансии на HH")  # Для связи с API
    url = models.URLField(max_length=500, verbose_name="Ссылка на вакансию", blank=True, null=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return f"{self.title} ({self.company_name or 'Без компании'})"