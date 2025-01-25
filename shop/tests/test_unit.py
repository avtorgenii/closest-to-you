from django.test import TestCase
from decimal import Decimal

from model_bakery import baker

from shop.services import add_courier_compensation, accept_complaint_service


class AddCourierCompensationTests(TestCase):
    def setUp(self):
        self.courier_role = baker.make('shop.WorkerRole', name='Courier')

        self.courier = baker.make('shop.Worker', role=self.courier_role)
        self.new_courier = baker.make('shop.Worker', role_id=self.courier_role.id)

        self.incident = baker.make(
            'shop.Incident',
            deliverer=self.courier,
            delivery__order__client__user__username='test_client',
            delivery_leave_place__name='By door',
            delivery_stage__name='In Transit'
        )

    def test_valid(self):
        success, _ = add_courier_compensation(self.courier.id, '50')
        self.incident.refresh_from_db() # always needed because Django uses attribute-level caching, and we are working on different instance here (one in the test, another in the service)
        self.assertTrue(success)
        self.assertEqual(self.incident.deliverer_compensation, Decimal('50'))

    def test_negative(self):
        success, error = add_courier_compensation(self.courier.id, '-10')
        self.assertFalse(success)
        self.assertIn('negative', error)

    def test_invalid(self):
        success, error = add_courier_compensation(self.courier.id, 'abc')
        self.assertFalse(success)
        self.assertIn('Invalid', error)

    def test_no_incident(self):
        success, error = add_courier_compensation(self.new_courier.id, '100')
        self.assertFalse(success)
        self.assertIn('No incident', error)


class AcceptComplaintServiceTest(TestCase):
    def setUp(self):
        self.worker = baker.make('shop.Worker', role__name='Support')
        self.client = baker.make('shop.Client')
        self.order = baker.make('shop.Order', client=self.client, total_price=Decimal('100.00'))
        self.complaint = baker.make('shop.Complaint', client=self.client, order=self.order)

    def test_valid_compensation(self):
        initial_comp = self.client.compensations
        accept_complaint_service(self.complaint, self.worker, '50.00', False)

        self.client.refresh_from_db()
        self.assertEqual(self.client.compensations, initial_comp + Decimal('50'))
        self.assertEqual(self.complaint.resolution, 'Accepted')

    def test_full_refund(self):
        initial_comp = self.client.compensations
        accept_complaint_service(self.complaint, self.worker, '0', True)

        self.client.refresh_from_db()
        self.assertEqual(self.client.compensations, initial_comp + self.order.total_price)

    def test_combined_compensation_refund(self):
        initial_comp = self.client.compensations
        accept_complaint_service(self.complaint, self.worker, '25.50', True)

        expected = self.order.total_price + Decimal('25.50')
        self.client.refresh_from_db()
        self.assertEqual(self.client.compensations, initial_comp + expected)

    def test_invalid_compensation_string(self):
        initial_comp = self.client.compensations
        accept_complaint_service(self.complaint, self.worker, 'abc', False)

        self.client.refresh_from_db()
        self.assertEqual(self.client.compensations, initial_comp + Decimal('0'))

    def test_negative_compensation(self):
        initial_comp = self.client.compensations
        accept_complaint_service(self.complaint, self.worker, '-30', False)

        self.client.refresh_from_db()
        self.assertEqual(self.client.compensations, initial_comp + Decimal('-30'))

    def test_refund_without_order(self):
        complaint_without_order = baker.make('shop.Complaint', client=self.client, order=None)

        with self.assertRaises(AttributeError):
            accept_complaint_service(complaint_without_order, self.worker, '0', True)
