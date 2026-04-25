import django_filters

from .models import Comment, Task


class TaskFilter(django_filters.FilterSet):
    deadline_before = django_filters.DateFilter(field_name='deadline', lookup_expr='lte')
    deadline_after = django_filters.DateFilter(field_name='deadline', lookup_expr='gte')

    class Meta:
        model = Task
        fields = ['project', 'status', 'priority', 'assignee', 'deadline']


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = ['task']
