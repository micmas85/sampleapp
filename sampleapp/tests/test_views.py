import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import WorkOrder
from ..serializers import WorkOrderCreateSerializer, WorkOrderSerializer
from django.contrib.auth.models import User



class GetAllWorkOrdersTest(TestCase):
    """ Test module for GET all work orderss API """

    def setUp(self):
        username = "test2"
        password = "test123456"
        self.user = User.objects.create(username=username, is_superuser=True, is_active = True)
        self.user.set_password(password)
        self.user.save()
        self.client = Client()
        self.client.force_login(user=self.user)
        user1 = User.objects.create(username='testuser1')
        user2 = User.objects.create(username='testuser2')
        WorkOrder.objects.create(
            title='title1', description='description1', created_by=user1, assigned_to=user2)
        WorkOrder.objects.create(
            title='title2', description='description2', created_by=user1, assigned_to=user2)
        WorkOrder.objects.create(
            title='title3', description='description3', created_by=user1, assigned_to=user2)
        WorkOrder.objects.create(
            title='title4', description='description4', created_by=user2, assigned_to=user1)

    def test_get_all_work_orders(self):
        response = self.client.get(reverse('work_order_list'))
        work_orders = WorkOrder.objects.all()
        serializer = WorkOrderSerializer(work_orders, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleWorkOrderTest(TestCase):
    """ Test module for GET single work order API """

    def setUp(self):
        username = "test2"
        password = "test123456"
        self.user = User.objects.create(username=username, is_superuser=True, is_active = True)
        self.user.set_password(password)
        self.user.save()
        self.client = Client()
        self.client.force_login(user=self.user)
        
        user1 = User.objects.create(username='testuser12')
        user1.set_password('1X<ISRUkw+tuK1')
        user1.save()
        user2 = User.objects.create(
            username='testuser22', password='1X<ISRUkw+tuK2')

        self.work_order1 = WorkOrder.objects.create(
            title='title1', description='description1', created_by=user1, assigned_to=user2)
        self.work_order2 = WorkOrder.objects.create(
            title='title2', description='description2', created_by=user1, assigned_to=user2)

    def test_get_valid_single_work_order(self):
        response = self.client.get(
            reverse('detail_work_order', kwargs={'pk': self.work_order1.pk}))
        work_order = WorkOrder.objects.get(pk=self.work_order1.pk)
        serializer = WorkOrderSerializer(work_order)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_work_order(self):
        response = self.client.get(reverse('detail_work_order', kwargs={'pk': 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateWorkOrderTest(TestCase):
    """ Test module for inserting a new work order """

    def setUp(self):
        username = "test2"
        password = "test123456"
        self.user = User.objects.create(username=username, is_superuser=True, is_active = True)
        self.user.set_password(password)
        self.user.save()
        self.client = Client()
        self.client.force_login(user=self.user)

        self.valid_payload = {
            'title': 'Example Title',
            'description': 'Description lorem ipsum lorem ipsum lorem ipsum lorem ipsum'
        }
        self.invalid_payload = {
            'title': '',
            'description': ''
        }

    def test_create_valid_work_order(self):
        response = self.client.post(
            reverse('create_work_order'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_work_order(self):
        response = self.client.post(
            reverse('create_work_order'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
