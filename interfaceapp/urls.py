from django.urls import path
from interfaceapp.views import logica
from interfaceapp.views import logica_paciente
from interfaceapp.views import logica_profesionalSalud
from interfaceapp.views import logica_director

urlpatterns = [
    path('', logica.vista_login),

    path("principal_paciente/<str:documento>/", logica_paciente.vista_principal_paciente, name="principal_paciente"),
    path("principal_profesionalSalud/<str:documento>/", logica_profesionalSalud.vista_principal_profesionalSalud, name="principal_profesionalSalud"),
    path('principal_director/<str:documento>/', logica_director.vista_principal_director, name="principal_director"),

    path("historia_clinica/<str:documento>/", logica_paciente.vista_historia_clinica, name = "historia_clinica"),
    path("agregar_adenda/<str:documento>/", logica_profesionalSalud.vista_agregar_adenda, name="agregar_adenda"),

    path("pagina_error/", logica.vista_error, name="pagina_error")
]

