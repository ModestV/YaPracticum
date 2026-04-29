from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment, Project, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода пользователя"""

    class Meta:
        """Поля пользователя для ответа"""

        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Поля для создания пользователя"""

        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        """Создаёт пользователя с хешированным паролем"""

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""

    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        """Поля проекта для API"""

        model = Project
        fields = ['id', 'name', 'description', 'owner', 'members', 'created_at']
        read_only_fields = ['id', 'owner', 'members', 'created_at']

    def create(self, validated_data):
        """Создаёт проект и добавляет владельца в участники"""

        request = self.context['request']
        project = Project.objects.create(owner=request.user, **validated_data)
        project.members.add(request.user)
        return project


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""

    author = UserSerializer(read_only=True)

    class Meta:
        """Поля задачи для API"""

        model = Task
        fields = [
            'id',
            'project',
            'title',
            'description',
            'author',
            'assignee',
            'status',
            'priority',
            'deadline',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Проверяет доступ к проекту и исполнителя задачи"""

        request = self.context['request']
        project = attrs.get('project') or getattr(self.instance, 'project', None)
        assignee = attrs.get('assignee') or getattr(self.instance, 'assignee', None)

        if project and not project.members.filter(id=request.user.id).exists():
            raise serializers.ValidationError('Вы не состоите в этом проекте')

        if assignee and project and not project.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError({'assignee': 'Исполнитель должен быть участником проекта'})

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария"""

    author = UserSerializer(read_only=True)

    class Meta:
        """Поля комментария для API"""

        model = Comment
        fields = ['id', 'task', 'author', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate(self, attrs):
        """Проверяет доступ пользователя к задаче комментария"""

        request = self.context['request']
        task = attrs.get('task') or getattr(self.instance, 'task', None)

        if task and not task.project.members.filter(id=request.user.id).exists():
            raise serializers.ValidationError({'task': 'Вы не состоите в проекте этой задачи'})

        return attrs
