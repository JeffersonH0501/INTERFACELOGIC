import requests
from django.shortcuts import render, redirect
from django.urls import reverse

def vista_principal_director(request, documento):

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
            }

            request.session["usuario"] = usuario

            if usuario["tipo"] == "director":
                return render(request, "pagina_principal_director.html", usuario)
            else:
                request.session["mensaje_error"] = f"Error al cargar la pagina ya que el {documento}  no corresponde a un director"

        else:
            request.session["mensaje_error"] = f"Error ({respuestaHttp.status_code}) al cargar la página del director"

    except requests.exceptions.RequestException as e:
        request.session["mensaje_error"] = "Error al cargar la pagina del director"
        
    return redirect(reverse("pagina_error"))