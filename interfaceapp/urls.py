from django.urls import path
from interfaceapp.views import logica
from interfaceapp.views import logica_paciente
from interfaceapp.views import logica_profesionalSalud
from interfaceapp.views import logica_director

urlpatterns = [
    path('', logica.vista_login),

    path("paciente/", logica_paciente.vista_principal_paciente, name="paciente"),
    path("profesionalSalud/", logica_profesionalSalud.vista_principal_profesionalSalud, name="profesionalSalud"),
    path("director/", logica_director.vista_principal_director, name="director"),

    path("paciente/historia_clinica/", logica_paciente.vista_historia_clinica, name = "paciente_historia_clinica"),
    path('profesionalSalud/consultar_historia/', logica_profesionalSalud.vista_consultar_historia, name='profesionalSalud_consultar_historia'),

    path("profesionalSalud/agregar_adenda", logica_profesionalSalud.vista_agregar_adenda, name="profesionalSalud_agregar_adenda"),

    path("pagina_error/", logica.vista_error, name="pagina_error")
]

