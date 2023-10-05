from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.vista_login, name='login'),
    #path('login/', views.login_view, name='login'),
    path('pagina_principal/', views.vista_principal, name='principal'),  # Define la URL de la página principal
]

