from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('menu/', views.menu_view, name='menu'),
    path('book/', views.book_table_view, name='book_table'),
    path('review/add/', views.add_review_view, name='add_review'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints
    path('api/table-status/', views.api_table_status, name='api_table_status'),
    
    # Admin Panel custom views
    path('admin-panel/login/', views.custom_admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.custom_admin_logout_view, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/menu/', views.admin_menu_list, name='admin_menu_list'),
    path('admin-panel/menu/add/', views.admin_menu_add, name='admin_menu_add'),
    path('admin-panel/menu/edit/<int:pk>/', views.admin_menu_edit, name='admin_menu_edit'),
    path('admin-panel/menu/delete/<int:pk>/', views.admin_menu_delete, name='admin_menu_delete'),
    path('admin-panel/settings/', views.admin_settings_view, name='admin_settings'),
]

