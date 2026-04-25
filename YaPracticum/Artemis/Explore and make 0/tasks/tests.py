from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Project, Task

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_get_token(self):
        register_response = self.client.post(
            reverse('register'),
            {
                'username': 'maria',
                'password': 'testpass123',
                'email': 'maria@example.com',
            },
            format='json',
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', register_response.data)

        token_response = self.client.post(
            reverse('token'),
            {
                'username': 'maria',
                'password': 'testpass123',
            },
            format='json',
        )

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', token_response.data)


class ProjectAccessTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='ivan', password='pass123')
        self.outsider = User.objects.create_user(username='alex', password='pass123')

    def test_owner_added_to_members_and_outsider_cannot_see_project(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            reverse('project-list'),
            {
                'name': 'Alpha',
                'description': 'Main project',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data['id'])
        self.assertTrue(project.members.filter(id=self.owner.id).exists())

        self.client.force_authenticate(self.outsider)
        detail_response = self.client.get(reverse('project-detail', args=[project.id]))
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)


class TaskTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='ivan', password='pass123')
        self.author = User.objects.create_user(username='maria', password='pass123')
        self.assignee = User.objects.create_user(username='alex', password='pass123')
        self.other = User.objects.create_user(username='olga', password='pass123')

        self.project = Project.objects.create(name='Alpha', description='Project', owner=self.owner)
        self.project.members.add(self.owner, self.author, self.assignee)

        self.task = Task.objects.create(
            project=self.project,
            title='First task',
            description='Old description',
            author=self.author,
            assignee=self.assignee,
            status='todo',
            priority='medium',
            deadline=date.today() + timedelta(days=7),
        )

    def test_cannot_assign_task_to_user_outside_project(self):
        self.client.force_authenticate(self.author)
        response = self.client.post(
            reverse('task-list'),
            {
                'project': self.project.id,
                'title': 'Bug fix',
                'description': 'Need to fix it',
                'assignee': self.other.id,
                'status': 'todo',
                'priority': 'high',
                'deadline': str(date.today() + timedelta(days=3)),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assignee', response.data)

    def test_assignee_can_change_only_status_and_priority(self):
        self.client.force_authenticate(self.assignee)

        status_response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {'status': 'in_progress'},
            format='json',
        )
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)

        description_response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {'description': 'New text'},
            format='json',
        )
        self.assertEqual(description_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_change_description_and_delete_task(self):
        self.client.force_authenticate(self.author)

        update_response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {'description': 'Updated by author'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(reverse('task-detail', args=[self.task.id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_owner_can_change_any_task_field(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {
                'title': 'Updated title',
                'priority': 'high',
                'status': 'done',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated title')
        self.assertEqual(self.task.status, 'done')


class CommentTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='ivan', password='pass123')
        self.member = User.objects.create_user(username='maria', password='pass123')
        self.outsider = User.objects.create_user(username='alex', password='pass123')

        self.project = Project.objects.create(name='Alpha', description='Project', owner=self.owner)
        self.project.members.add(self.owner, self.member)
        self.task = Task.objects.create(
            project=self.project,
            title='First task',
            description='Task text',
            author=self.owner,
            assignee=self.member,
            status='todo',
            priority='medium',
            deadline=date.today() + timedelta(days=2),
        )

    def test_only_project_member_can_create_comment(self):
        self.client.force_authenticate(self.member)
        ok_response = self.client.post(
            reverse('comment-list'),
            {
                'task': self.task.id,
                'text': 'Need more details',
            },
            format='json',
        )
        self.assertEqual(ok_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

        self.client.force_authenticate(self.outsider)
        bad_response = self.client.post(
            reverse('comment-list'),
            {
                'task': self.task.id,
                'text': 'I should not comment here',
            },
            format='json',
        )
        self.assertEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST)

# Create your tests here.
