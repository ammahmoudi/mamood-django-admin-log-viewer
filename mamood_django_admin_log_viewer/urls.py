from django.urls import path
from . import views

app_name = 'mamood_django_admin_log_viewer'

urlpatterns = [
    path('', views.log_list_view, name='log_list'),
    path('<str:filename>/', views.log_detail_view, name='log_detail'),
    path('<str:filename>/ajax/', views.log_ajax_view, name='log_ajax'),
]
