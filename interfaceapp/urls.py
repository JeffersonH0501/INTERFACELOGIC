from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_login, name='login'),
    path('pagina_principal/', views.vista_principal, name='principal')
]

