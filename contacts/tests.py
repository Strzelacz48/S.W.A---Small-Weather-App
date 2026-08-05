from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact, ContactStatusChoices


class ContactModelConstraintsTests(TestCase):
    def setUp(self):
        # "New" already exists from the 0002_seed_initial_statuses data
        # migration, which runs against the test DB too — get_or_create
        # avoids colliding with it.
        self.status, _ = ContactStatusChoices.objects.get_or_create(name="New")
        Contact.objects.create(
            first_name="Jan", last_name="Kowalski", phone="111222333",
            email="jan@example.com", city="Warszawa", status=self.status,
        )

    def test_duplicate_phone_raises_integrity_error(self):
        # transaction.atomic() gives the failing insert its own savepoint,
        # so the outer test transaction (and Postgres) isn't left "aborted"
        # once the IntegrityError is raised.
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Contact.objects.create(
                    first_name="Anna", last_name="Nowak", phone="111222333",
                    email="anna@example.com", city="Krakow", status=self.status,
                )

    def test_duplicate_email_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Contact.objects.create(
                    first_name="Piotr", last_name="Wisniewski", phone="999999999",
                    email="jan@example.com", city="Gdansk", status=self.status,
                )


class ContactListViewTests(TestCase):
    def setUp(self):
        self.status, _ = ContactStatusChoices.objects.get_or_create(name="New")
        self.zawadzka = Contact.objects.create(
            first_name="Anna", last_name="Zawadzka", phone="600100001",
            email="anna@example.com", city="Warszawa", status=self.status,
        )
        self.adamski = Contact.objects.create(
            first_name="Bartek", last_name="Adamski", phone="600100002",
            email="bartek@example.com", city="Lodz", status=self.status,
        )

    def test_list_view_status_code(self):
        response = self.client.get(reverse("contacts:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_sorts_by_last_name_ascending(self):
        response = self.client.get(reverse("contacts:list"), {"sort": "last_name"})
        last_names = [c.last_name for c in response.context["contacts"]]
        self.assertEqual(last_names, ["Adamski", "Zawadzka"])

    def test_list_view_sorts_by_last_name_descending(self):
        response = self.client.get(reverse("contacts:list"), {"sort": "-last_name"})
        last_names = [c.last_name for c in response.context["contacts"]]
        self.assertEqual(last_names, ["Zawadzka", "Adamski"])

    def test_list_view_rejects_invalid_sort_field(self):
        response = self.client.get(reverse("contacts:list"), {"sort": "not_a_real_field"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_sort"], "-created_at")


class ContactAPITests(TestCase):
    def setUp(self):
        self.status, _ = ContactStatusChoices.objects.get_or_create(name="New")
        self.contact = Contact.objects.create(
            first_name="Jan", last_name="Kowalski", phone="111222333",
            email="jan@example.com", city="Warszawa", status=self.status,
        )

    def test_list_endpoint_returns_contacts(self):
        response = self.client.get(reverse("contact-list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "jan@example.com")

    def test_create_endpoint_persists_contact(self):
        response = self.client.post(
            reverse("contact-list"),
            data={
                "first_name": "Anna", "last_name": "Nowak", "phone": "999888777",
                "email": "anna@example.com", "city": "Krakow", "status": self.status.id,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contact.objects.count(), 2)