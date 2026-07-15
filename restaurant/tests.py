from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Category, MenuItem, Reservation, Review, RestaurantTable

class CategoryAndMenuItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Appetizers",
            slug="appetizers",
            description="Starters to share"
        )
        self.item = MenuItem.objects.create(
            name="Garlic Bread",
            description="Baked bread with fresh garlic",
            price=250.00,
            category=self.category,
            is_available=True
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), "Appetizers")
        self.assertEqual(self.category.slug, "appetizers")

    def test_menu_item_creation(self):
        self.assertEqual(str(self.item), "Garlic Bread")
        self.assertEqual(self.item.get_image_url, "/static/restaurant/images/placeholder.jpg")

class ReservationModelTest(TestCase):
    def setUp(self):
        # Create a valid table
        self.table = RestaurantTable.objects.create(table_number=1, capacity=4, table_type="Standard")
        self.valid_date = timezone.localdate() + timedelta(days=1)
        self.past_date = timezone.localdate() - timedelta(days=1)

    def test_valid_reservation(self):
        booking = Reservation(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            number_of_guests=4,
            date=self.valid_date,
            time_slot="7:00 PM",
            table=self.table
        )
        # Should not raise any errors
        booking.save()
        self.assertEqual(Reservation.objects.count(), 1)

    def test_past_date_reservation_fails(self):
        booking = Reservation(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            number_of_guests=4,
            date=self.past_date,
            time_slot="7:00 PM",
            table=self.table
        )
        with self.assertRaises(ValidationError):
            booking.save()

    def test_table_capacity_exceeded_fails(self):
        booking = Reservation(
            name="Too Many Guests",
            email="too@many.com",
            phone="1234567890",
            number_of_guests=10,  # Table capacity is only 4
            date=self.valid_date,
            time_slot="7:00 PM",
            table=self.table
        )
        with self.assertRaises(ValidationError):
            booking.save()

    def test_double_booking_fails(self):
        # Create first valid booking
        Reservation.objects.create(
            name="First Guest",
            email="first@guest.com",
            phone="1234567890",
            number_of_guests=2,
            date=self.valid_date,
            time_slot="7:00 PM",
            table=self.table
        )
        
        # Try to book the same table, date, and slot
        second_booking = Reservation(
            name="Second Guest",
            email="second@guest.com",
            phone="0987654321",
            number_of_guests=2,
            date=self.valid_date,
            time_slot="7:00 PM",
            table=self.table
        )
        with self.assertRaises(ValidationError):
            second_booking.save()

class RestaurantViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Mains", slug="mains")
        self.item = MenuItem.objects.create(
            name="Steak",
            description="Seared ribeye",
            price=850.00,
            category=self.category,
            is_available=True,
            is_special=True
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taste Haven")
        self.assertTemplateUsed(response, 'restaurant/home.html')

    def test_menu_page_status_and_filters(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Steak")
        
        # Test active category filter
        response_filtered = self.client.get(reverse('menu') + '?category=mains')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertContains(response_filtered, "Steak")

