from django.urls import path
from . import views
from .pdf_views import note_pdf

app_name = 'notes'

urlpatterns = [
    # Notes CRUD
    path('', views.note_list, name='note_list'),
    path('create/', views.note_create, name='note_create'),
    path('<int:pk>/', views.note_detail, name='note_detail'),
    path('<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('<int:pk>/delete/', views.note_delete, name='note_delete'),

    # PDF export
    path('<int:pk>/pdf/', note_pdf, name='note_pdf'),

    # Categories CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Tags CRUD
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
]
