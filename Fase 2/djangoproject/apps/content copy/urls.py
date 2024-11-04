# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('subject/<int:subject_id>/files/', views.content_list, name='content_list'),
    path('subject/<int:subject_id>/add_content/', views.add_content, name='add_content'),
    path('content/<int:content_id>/detail/', views.content_detail, name='content_detail'),
]
