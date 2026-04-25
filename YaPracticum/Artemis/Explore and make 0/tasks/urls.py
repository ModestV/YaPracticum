from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, CustomAuthTokenView, ProjectViewSet, RegisterView, TaskViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('tasks', TaskViewSet, basename='task')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomAuthTokenView.as_view(), name='token'),
    path('', include(router.urls)),
]
