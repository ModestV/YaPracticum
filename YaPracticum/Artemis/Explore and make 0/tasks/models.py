from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    """Модель проекта"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки сортировки проектов"""

        ordering = ['-created_at']

    def __str__(self):
        """Возвращает название проекта"""

        return self.name


class Task(models.Model):
    """Модель задачи"""

    STATUS_CHOICES = [
        ('todo', 'To do'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Настройки сортировки задач"""

        ordering = ['deadline', '-created_at']

    def __str__(self):
        """Возвращает заголовок задачи"""

        return self.title


class Comment(models.Model):
    """Модель комментария к задаче"""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки сортировки комментариев"""

        ordering = ['created_at']

    def __str__(self):
        """Возвращает краткое описание комментария"""

        return f'Комментарий {self.author} к {self.task}'
