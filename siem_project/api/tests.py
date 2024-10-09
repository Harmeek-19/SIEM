from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Alert
from django.contrib.auth import get_user_model

class AlertAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.alert = Alert.objects.create(title='Test Alert', description='This is a test', severity='High')

    def test_list_alerts(self):
        response = self.client.get(reverse('alert-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_alert(self):
        data = {'title': 'New Alert', 'description': 'This is a new alert', 'severity': 'Medium'}
        response = self.client.post(reverse('alert-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alert.objects.count(), 2)

    def test_retrieve_alert(self):
        response = self.client.get(reverse('alert-detail', kwargs={'pk': self.alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Alert')

    def test_update_alert(self):
        data = {'title': 'Updated Alert', 'description': 'This is an updated alert', 'severity': 'Low'}
        response = self.client.put(reverse('alert-detail', kwargs={'pk': self.alert.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.title, 'Updated Alert')

    def test_delete_alert(self):
        response = self.client.delete(reverse('alert-detail', kwargs={'pk': self.alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Alert.objects.count(), 0)
