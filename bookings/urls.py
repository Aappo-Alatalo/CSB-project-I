from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book/', views.book, name='book'),
    path('directory/', views.directory, name='directory'),
    path('reservation/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]
