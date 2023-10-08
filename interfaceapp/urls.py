from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_login, name='login'),
    path('principal_profesionalSalud/', views.vista_principal_profesionalSalud, name='principal_profesionalSalud'),
    path('principal_paciente/', views.vista_principal_paciente, name='principal_paciente'),
    path('principal_director/', views.vista_principal_director, name='principal_director')
]

