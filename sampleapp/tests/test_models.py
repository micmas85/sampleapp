from django.test import TestCase
from sampleapp.models import WorkOrder


class WorkOrderTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        WorkOrder.objects.create(title="test", description="this is only a test")
        
    def test_title_label(self):
        work_order = WorkOrder.objects.get(id=1)
        field_label = work_order._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'Title')

    def test_description_label(self):
        work_order = WorkOrder.objects.get(id=1)
        field_label = work_order._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'Description')
      
    def test_title_max_length(self):
        work_order = WorkOrder.objects.get(id=1)
        max_length = work_order._meta.get_field('title').max_length
        self.assertEqual(max_length, 64)
        
    def test_status_default_value(self):
        work_order = WorkOrder.objects.get(id=1)
        status = work_order.status
        self.assertEqual(status, "NEW")
        
    def test_created_at_not_none(self):
        work_order = WorkOrder.objects.get(id=1)
        created_at = work_order.created_at
        self.assertIsNotNone(created_at)
        
    def test_updated_at_not_none(self):
        work_order = WorkOrder.objects.get(id=1)
        updated_at = work_order.updated_at
        self.assertIsNotNone(updated_at)
        
    def test_assigned_to_none(self):
        work_order = WorkOrder.objects.get(id=1)
        assigned_to = work_order.assigned_to
        self.assertIsNone(assigned_to)