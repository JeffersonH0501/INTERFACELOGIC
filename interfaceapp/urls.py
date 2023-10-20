from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_login),
    path('principal_profesionalSalud/<str:documento>/', views.vista_principal_profesionalSalud, name='principal_profesionalSalud'),
    path('principal_paciente/<str:documento>/', views.vista_principal_paciente, name='principal_paciente'),
    path('principal_director/<str:documento>/', views.vista_principal_director, name='principal_director'),
    path('pagina_error/', views.vista_error, name='pagina_error')
]

