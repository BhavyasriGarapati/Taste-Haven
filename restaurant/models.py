from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import random
import string

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Fallback image URL if no file is uploaded")
    is_available = models.BooleanField(default=True)
    is_special = models.BooleanField(default=False, help_text="Featured on homepage as chef special")
    is_veg = models.BooleanField(default=True, help_text="Checked for Veg, unchecked for Non-Veg")
    is_popular = models.BooleanField(default=False)
    is_chef_recommendation = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_new_arrival = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return "/static/restaurant/images/placeholder.jpg"

    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return round(self.price - discount_amount, 2)
        return self.price

class RestaurantTable(models.Model):
    TABLE_TYPES = [
        ('Standard', 'Standard (2-4 seats)'),
        ('Family', 'Family (6-10 seats)'),
        ('Couple', 'Couple (2 seats)'),
        ('VIP', 'VIP Private Lounge'),
    ]
    table_number = models.IntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    table_type = models.CharField(max_length=20, choices=TABLE_TYPES, default='Standard')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number} ({self.table_type} - {self.capacity} seats)"

class Reservation(models.Model):
    TIME_SLOTS = [
        ('11:00 AM', '11:00 AM'),
        ('12:00 PM', '12:00 PM'),
        ('1:00 PM', '1:00 PM'),
        ('2:00 PM', '2:00 PM'),
        ('3:00 PM', '3:00 PM'),
        ('4:00 PM', '4:00 PM'),
        ('5:00 PM', '5:00 PM'),
        ('6:00 PM', '6:00 PM'),
        ('7:00 PM', '7:00 PM'),
        ('8:00 PM', '8:00 PM'),
        ('9:00 PM', '9:00 PM'),
        ('10:00 PM', '10:00 PM'),
        ('11:00 PM', '11:00 PM'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOTS)
    table = models.ForeignKey(RestaurantTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    special_requests = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validate that the booking date is not in the past
        if self.date and self.date < timezone.localdate():
            raise ValidationError("You cannot book a table in the past.")
        
        # Phone validation
        if self.phone and not self.phone.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValidationError("Please enter a valid mobile number containing only digits.")
        
        if self.table:
            # Table capacity check
            if self.number_of_guests > self.table.capacity:
                raise ValidationError(f"Table {self.table.table_number} can seat at most {self.table.capacity} guests.")
            
            # Prevent double booking for same date, time slot, and table
            duplicate_bookings = Reservation.objects.filter(
                date=self.date,
                time_slot=self.time_slot,
                table=self.table,
                status__in=['confirmed', 'pending']
            ).exclude(pk=self.pk)
            
            if duplicate_bookings.exists():
                raise ValidationError(
                    f"Table {self.table.table_number} has already been reserved for the selected date and time. Please choose another available table."
                )

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = 'TH-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.date} @ {self.time_slot} (Table {self.table.table_number if self.table else 'Unassigned'})"

class PreOrder(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='pre_order')
    grand_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pre-order for Reservation {self.reservation.reference_number} (Total: ₹{self.grand_total})"

class PreOrderItem(models.Model):
    pre_order = models.ForeignKey(PreOrder, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Snapshot of price at order time

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} under Pre-order {self.pre_order.id}"

class Review(models.Model):
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    is_visible = models.BooleanField(default=True, help_text="Toggle visibility on homepage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} - {self.rating} Stars"


