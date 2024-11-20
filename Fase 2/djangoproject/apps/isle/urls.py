from django.urls import path
from . import views
from .views import RepresentativeDashboardView

urlpatterns = [
    path('index/', views.carousel_view, name='index'),
    path('', views.carousel_Form_view, name='form'),
    path('list/', views.carousel_update_delete, name='list'),
    path('update/<int:pk>/', views.carousel_update, name='update'),  
    path('api/', views.CarouselItemList.as_view(), name='carousel-item-list'),
    path('api/<int:pk>/', views.CarouselItemDetail.as_view(), name='carousel-item-detail'),
    path('dashboard/', RepresentativeDashboardView.as_view(), name='representative_dashboard'),

    
]