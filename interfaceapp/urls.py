from django.urls import path
from interfaceapp.views import views
#from . import views

urlpatterns = [
    path('', views.vista_login),
    path('principal_paciente/<str:documento>/', views.vista_principal_paciente, name='principal_paciente'),
    path('historia_clinica/<str:documento>/', views.vista_historiaClinica_paciente, name = 'historia_clinica'),
    path('principal_director/<str:documento>/', views.vista_principal_director, name='principal_director'),
    path('agregar_adenda/', views.vista_agregar_adenda, name='vista_agregar_adenda'),
    path('pagina_error/', views.vista_error, name='pagina_error')
]

