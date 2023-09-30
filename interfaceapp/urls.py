from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('pagina_principal/', views.pagina_principal, name='pagina_principal'),  # Define la URL de la página principal
]

