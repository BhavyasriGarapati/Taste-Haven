from django import forms
from .models import Reservation, Review

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'number_of_guests', 'date', 'time_slot', 'table', 'special_requests']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile Number (e.g. 9876543210)',
                'required': 'required'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'required': 'required',
                'id': 'id_number_of_guests'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required',
                'id': 'id_date'
            }),
            'time_slot': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'id': 'id_time_slot'
            }),
            'table': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_table',
                'style': 'display:none;'  # We hide it and select via clicking visual cards
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements? (e.g., wheelchair access, food allergies, high chair for kids)'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': 'required'
            }),
            'rating': forms.Select(
                choices=[(i, f"{i} ★" + ("★" * (i-1) if i > 1 else "")) for i in range(5, 0, -1)],
                attrs={
                    'class': 'form-control',
                    'required': 'required'
                }
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about your experience, the food, and service...',
                'required': 'required'
            }),
        }

from .models import MenuItem

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'image_url', 'is_available', 'is_special', 'is_veg', 'is_popular', 'is_chef_recommendation', 'discount_percentage', 'is_new_arrival']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'required'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional fallback URL'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Admin Username',
        'required': 'required'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Admin Password',
        'required': 'required'
    }))

