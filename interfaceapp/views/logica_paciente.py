import requests
from django.shortcuts import render, redirect
from django.urls import reverse

def vista_principal_paciente(request):

    documento = request.session.get("usuario").get("documento")

    try:
        respuestaHttp = requests.post("http://10.128.0.8:8000/usuario/", json={"documento": documento})

        if respuestaHttp.status_code == 200:

            usuarioJson = respuestaHttp.json()

            usuario = {
                "documento": usuarioJson.get("documento"),
                "clave": usuarioJson.get("clave"),
                "tipo": usuarioJson.get("tipo"),
                "foto": usuarioJson.get("foto"),
                "nombre": usuarioJson.get("nombre"),
                "edad": usuarioJson.get("edad"),
                "telefono": usuarioJson.get("telefono"),
                "sexo": usuarioJson.get("sexo"),
                "historia_clinica": {
                    'diagnosticos': usuarioJson.get('historia_clinica').get('diagnosticos'),
                    'tratamientos': usuarioJson.get('historia_clinica').get('tratamientos'),
                    'notas': usuarioJson.get('historia_clinica').get('notas')
                },
                "adendas": []
            }

            for adenda in usuarioJson.get("adendas"):
                usuario["adendas"].append(adenda)

            request.session["usuario"] = usuario

            if usuario["tipo"] == "paciente":
                return render(request, "pagina_principal_paciente.html", usuario)

            else:
                request.session["mensaje_error"] = f"Error al cargar la pagina ya que el {documento} no corresponde a un paciente"

        else:
            request.session["mensaje_error"] = f"Error ({respuestaHttp.status_code}) al cargar la página del paciente"

    except requests.exceptions.RequestException as e:
        request.session["mensaje_error"] = "Error al cargar la pagina del paciente"
        
    return redirect(reverse("pagina_error"))

def vista_historia_clinica(request):

    usuario = request.session.get("usuario")

    if usuario["tipo"] == "paciente":
        return render(request, "pagina_historia_clinica.html", usuario)
    else:
        request.session["mensaje_error"] = f"Error al cargar la pagina ya que el {usuario['documento']} no corresponde a un paciente"
    
    return redirect(reverse("pagina_error"))