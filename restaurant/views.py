from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from datetime import datetime, time

from .models import Category, MenuItem, Reservation, Review, RestaurantTable, PreOrder, PreOrderItem
from .forms import ReservationForm, ReviewForm, MenuItemForm, AdminLoginForm

def home_view(request):
    specials = MenuItem.objects.filter(is_available=True, is_special=True)[:4]
    reviews = Review.objects.filter(is_visible=True).order_by('-created_at')[:4]
    review_form = ReviewForm()
    
    context = {
        'specials': specials,
        'reviews': reviews,
        'review_form': review_form,
        'current_year': timezone.now().year
    }
    return render(request, 'restaurant/home.html', context)

def menu_view(request):
    categories = Category.objects.all()
    items = MenuItem.objects.all()
    
    # 1. Search filter
    q = request.GET.get('q', '')
    if q:
        items = items.filter(name__icontains=q) | items.filter(description__icontains=q)
        
    # 2. Category filter
    selected_category_slug = request.GET.get('category', 'all')
    if selected_category_slug != 'all':
        items = items.filter(category__slug=selected_category_slug)
        
    # 3. Veg/Non-Veg filter
    food_type = request.GET.get('type', 'all')
    if food_type == 'veg':
        items = items.filter(is_veg=True)
    elif food_type == 'nonveg':
        items = items.filter(is_veg=False)
        
    # 4. Sort by price
    sort_price = request.GET.get('sort', '')
    if sort_price == 'asc':
        items = items.order_by('price')
    elif sort_price == 'desc':
        items = items.order_by('-price')
    else:
        # Default order (specials first, then newest)
        items = items.order_by('-is_special', '-is_popular', '-created_at')

    context = {
        'categories': categories,
        'items': items,
        'selected_category': selected_category_slug,
        'q': q,
        'food_type': food_type,
        'sort_price': sort_price,
    }
    return render(request, 'restaurant/menu.html', context)

def book_table_view(request):
    success = False
    reservation = None
    tables = RestaurantTable.objects.filter(is_active=True).order_by('table_number')
    menu_items = MenuItem.objects.all().order_by('category', 'name')
    
    # Define active/available time slots
    slots = [s[0] for s in Reservation.TIME_SLOTS]

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        pre_order_items_json = request.POST.get('pre_order_items', '[]')
        
        if form.is_valid():
            try:
                # Save reservation
                reservation = form.save(commit=False)
                
                # Check for duplicate table reservation backend-side
                duplicate = Reservation.objects.filter(
                    date=reservation.date,
                    time_slot=reservation.time_slot,
                    table=reservation.table,
                    status__in=['confirmed', 'pending']
                ).exists()
                
                if duplicate:
                    form.add_error('table', f"Table {reservation.table.table_number} has already been reserved for the selected date and time. Please choose another available table.")
                    raise ValidationError("Double booking prevented.")
                
                # Check working hours (11:00 AM to 11:00 PM)
                time_slot = reservation.time_slot
                # Slots are string choices: '11:00 AM', '12:00 PM', ..., '11:00 PM'
                # Handled correctly by Reservation.TIME_SLOTS definitions
                
                reservation.save()
                
                # Process Pre-Orders
                ordered_items = json.loads(pre_order_items_json)
                if ordered_items:
                    pre_order = PreOrder.objects.create(reservation=reservation)
                    grand_total = 0
                    for item in ordered_items:
                        m_item = get_object_or_404(MenuItem, id=item['id'])
                        if not m_item.is_available:
                            continue
                        qty = int(item['qty'])
                        price = m_item.final_price
                        sub = price * qty
                        grand_total += sub
                        PreOrderItem.objects.create(
                            pre_order=pre_order,
                            menu_item=m_item,
                            quantity=qty,
                            price=price
                        )
                    pre_order.grand_total = grand_total
                    pre_order.save()
                
                success = True
                messages.success(request, "Your table and pre-ordered food have been reserved successfully!")
                form = ReservationForm()
            except Exception as e:
                if str(e) != "Double booking prevented.":
                    messages.error(request, str(e).replace("[", "").replace("]", "").replace("'", ""))
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = ReservationForm()
        
    context = {
        'form': form,
        'success': success,
        'reservation': reservation,
        'tables': tables,
        'menu_items': menu_items,
        'time_slots': slots,
    }
    return render(request, 'restaurant/book.html', context)

def api_table_status(request):
    """
    AJAX API endpoint returning availability status for all tables for a given date and time slot.
    🟢 Available, 🔴 Booked, 🟡 Reserved Soon
    """
    date_str = request.GET.get('date')
    time_slot = request.GET.get('time_slot')
    
    if not date_str or not time_slot:
        return JsonResponse({'error': 'Missing date or time_slot parameter'}, status=400)
        
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    tables = RestaurantTable.objects.filter(is_active=True)
    table_statuses = []

    for t in tables:
        # Check if table is booked for this slot
        is_booked = Reservation.objects.filter(
            date=booking_date,
            time_slot=time_slot,
            table=t,
            status__in=['confirmed', 'pending']
        ).exists()
        
        # Check if table is reserved soon (booked in other slots on the same date)
        is_reserved_soon = False
        if not is_booked:
            is_reserved_soon = Reservation.objects.filter(
                date=booking_date,
                table=t,
                status__in=['confirmed', 'pending']
            ).exclude(time_slot=time_slot).exists()
            
        status = 'booked' if is_booked else ('reserved_soon' if is_reserved_soon else 'available')
        
        table_statuses.append({
            'id': t.id,
            'table_number': t.table_number,
            'capacity': t.capacity,
            'table_type': t.table_type,
            'status': status
        })
        
    return JsonResponse({'tables': table_statuses})

def custom_admin_login_view(request):
    """
    Custom branded admin login portal.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, "Welcome to Taste Haven Admin Dashboard.")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid admin credentials or permission denied.")
    else:
        form = AdminLoginForm()
        
    return render(request, 'restaurant/admin_login.html', {'form': form})

def custom_admin_logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@staff_member_required(login_url='admin_login')
def admin_dashboard_view(request):
    """
    Advanced Admin Reservation Dashboard with charts, revenue stats, and analysis.
    """
    today = timezone.localdate()
    
    # Basic reservation status lists
    res_today = Reservation.objects.filter(date=today).order_by('time_slot')
    res_upcoming = Reservation.objects.filter(date__gt=today).order_by('date', 'time_slot')
    res_cancelled = Reservation.objects.filter(status='cancelled').order_by('-date')[:10]
    res_completed = Reservation.objects.filter(status='completed').order_by('-date')[:10]
    
    # Financial Analytics (from pre-orders)
    total_rev = PreOrder.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
    today_rev = PreOrder.objects.filter(reservation__date=today).aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
    
    # Most Reserved Tables
    popular_tables = Reservation.objects.filter(status='confirmed').values('table__table_number')\
        .annotate(count=Count('id')).order_by('-count')[:5]
        
    # Most Ordered Food Items
    popular_foods = PreOrderItem.objects.values('menu_item__name')\
        .annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]
        
    # Peak Booking Times (Time Slot counts)
    peak_times = Reservation.objects.values('time_slot')\
        .annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'reservations_today': res_today,
        'upcoming_reservations': res_upcoming,
        'cancelled_reservations': res_cancelled,
        'completed_reservations': res_completed,
        'total_revenue': total_rev,
        'today_revenue': today_rev,
        'popular_tables': popular_tables,
        'popular_foods': popular_foods,
        'peak_times': peak_times,
        'today': today,
    }
    return render(request, 'restaurant/admin_dashboard.html', context)

def dashboard_view(request):
    """
    Staff Dashboard - VIEW only reservation sheets and view-only menu statuses.
    """
    today = timezone.localdate()
    
    # Filter reservations
    reservations_today = Reservation.objects.filter(date=today).order_by('time_slot')
    upcoming_reservations = Reservation.objects.filter(date__gt=today).order_by('date', 'time_slot')
    past_reservations = Reservation.objects.filter(date__lt=today).order_by('-date')[:15]
    
    # Statistics
    total_bookings = Reservation.objects.count()
    total_guests_today = Reservation.objects.filter(date=today, status='confirmed').aggregate(Sum('number_of_guests'))['number_of_guests__sum'] or 0
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0
    total_reviews = Review.objects.count()
    
    # Menu Items (VIEW only)
    menu_items = MenuItem.objects.all().order_by('category', 'name')
    
    context = {
        'reservations_today': reservations_today,
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
        'total_bookings': total_bookings,
        'total_guests_today': total_guests_today,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'menu_items': menu_items,
        'today': today,
    }
    return render(request, 'restaurant/dashboard.html', context)

# ----------------------------------------------------
# ADMIN MENU MANAGEMENT (CRUD)
# ----------------------------------------------------

@staff_member_required(login_url='admin_login')
def admin_menu_list(request):
    items = MenuItem.objects.all().order_by('category', 'name')
    return render(request, 'restaurant/admin_menu_list.html', {'items': items})

@staff_member_required(login_url='admin_login')
def admin_menu_add(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New food item added successfully!")
            return redirect('admin_menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'restaurant/admin_menu_form.html', {'form': form, 'title': 'Add Food Item'})

@staff_member_required(login_url='admin_login')
def admin_menu_edit(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{item.name}' updated successfully!")
            return redirect('admin_menu_list')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'restaurant/admin_menu_form.html', {'form': form, 'title': f"Edit '{item.name}'"})

@staff_member_required(login_url='admin_login')
def admin_menu_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    name = item.name
    item.delete()
    messages.success(request, f"'{name}' deleted successfully!")
    return redirect('admin_menu_list')

def add_review_view(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your valuable feedback!")
            return redirect('home')
        else:
            messages.error(request, "Failed to submit review. Please try again.")
    return redirect('home')

@staff_member_required(login_url='admin_login')
def admin_settings_view(request):
    """
    Custom Admin Settings page allowing credentials modification.
    """
    user = request.user
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_username:
            messages.error(request, "Username cannot be empty.")
        elif new_password and new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.username = new_username
            if new_password:
                user.set_password(new_password)
            user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, "Admin credentials updated successfully!")
            return redirect('admin_dashboard')
            
    return render(request, 'restaurant/admin_settings.html', {'username': user.username})



