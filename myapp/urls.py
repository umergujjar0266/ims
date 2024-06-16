from django.urls import path
from . import views
from .views import index, user_dashboard, admin_dashboard


urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('plan/', views.plan, name='plan'),
    path('alerts/', views.alert_list, name='alert_list'),
    path('user_contact/', views.user_contact, name='user_contact'),
    path('user_contact/success/', views.contact_success, name='contact_success'),
    path('index/', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/', user_dashboard, name='user_dashboard'),
    path('admin/', admin_dashboard, name='admin_dashboard'),
]