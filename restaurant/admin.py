from django.contrib import admin
from .models import Category, MenuItem, Reservation, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_special', 'created_at')
    list_filter = ('category', 'is_available', 'is_special')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_special')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time_slot', 'number_of_guests', 'phone', 'status', 'created_at')
    list_filter = ('date', 'time_slot', 'status')
    search_fields = ('name', 'email', 'phone', 'special_requests')
    list_editable = ('status',)
    date_hierarchy = 'date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible')
    search_fields = ('name', 'comment')
    list_editable = ('is_visible',)

