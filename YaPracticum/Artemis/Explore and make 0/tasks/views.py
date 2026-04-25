from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import CommentFilter, TaskFilter
from .models import Comment, Project, Task
from .serializers import (
    CommentSerializer,
    ProjectSerializer,
    TaskSerializer,
    UserRegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'token': token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomAuthTokenView(ObtainAuthToken):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
            }
        )


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(members=self.request.user).select_related('owner').prefetch_related('members').distinct()

    def _check_owner(self, project):
        if project.owner != self.request.user:
            raise PermissionDenied('Только владелец проекта может это делать.')

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        self._check_owner(project)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        project = self.get_object()
        self._check_owner(project)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        self._check_owner(project)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        project = self.get_object()
        self._check_owner(project)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'detail': 'Нужно передать user_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        project.members.add(user)
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        self._check_owner(project)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'detail': 'Нужно передать user_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if user == project.owner:
            return Response({'detail': 'Нельзя удалить владельца проекта.'}, status=status.HTTP_400_BAD_REQUEST)

        if Task.objects.filter(project=project, assignee=user).exists():
            return Response(
                {'detail': 'Нельзя удалить участника, на которого назначены задачи.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.members.remove(user)
        serializer = self.get_serializer(project)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        return (
            Task.objects.filter(project__members=self.request.user)
            .select_related('project', 'author', 'assignee')
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _get_allowed_fields(self, task):
        if self.request.user == task.project.owner:
            return None

        allowed_fields = set()
        if self.request.user == task.author:
            allowed_fields.add('description')
        if self.request.user == task.assignee:
            allowed_fields.update({'status', 'priority'})
        return allowed_fields

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        allowed_fields = self._get_allowed_fields(task)
        partial = kwargs.pop('partial', False)

        if allowed_fields is not None:
            request_fields = set(request.data.keys())
            if not request_fields:
                raise PermissionDenied('Нет данных для обновления.')
            if not request_fields.issubset(allowed_fields):
                raise PermissionDenied('Вы можете менять только разрешенные поля задачи.')
            partial = True

        serializer = self.get_serializer(task, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user != task.project.owner and request.user != task.author:
            raise PermissionDenied('Удалять задачу может владелец проекта или автор задачи.')
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    filterset_class = CommentFilter

    def get_queryset(self):
        return (
            Comment.objects.filter(task__project__members=self.request.user)
            .select_related('task', 'author', 'task__project')
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.author:
            raise PermissionDenied('Редактировать комментарий может только его автор.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.author:
            raise PermissionDenied('Редактировать комментарий может только его автор.')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.author and request.user != comment.task.project.owner:
            raise PermissionDenied('Удалять комментарий может его автор или владелец проекта.')
        return super().destroy(request, *args, **kwargs)

# Create your views here.
