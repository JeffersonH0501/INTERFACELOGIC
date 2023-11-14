import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from datetime import datetime

def vista_principal_profesionalSalud(request, documento):

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

            if usuario["tipo"] == "profesionalSalud":
                return render(request, "pagina_principal_profesionalSalud.html", usuario)
            else:
                request.session["mensaje_error"] = f"Error al cargar la pagina ya que el {documento}  no corresponde a un profesional de salud"

        else:
            request.session["mensaje_error"] = f"Error ({respuestaHttp.status_code}) al cargar la página del profesional de salud"

    except requests.exceptions.RequestException as e:
        request.session["mensaje_error"] = "Error al cargar la pagina del profesional de salud"
        
    return redirect(reverse("pagina_error"))

def vista_agregar_adenda(request, documento):

    usuario = request.session.get("usuario")

    if request.method == "POST":

        form = AdendaForm(request.POST)
        contexto = usuario.copy()

        if form.is_valid():

            documento_paciente = form.cleaned_data["documento_paciente"]
            fecha = datetime.now()
            fecha = fecha.strftime("%d-%m-%Y")
            tipo = form.cleaned_data["tipo"]
            descripcion = form.cleaned_data["descripcion"]

            informacion_adenda = {"documento_paciente": documento_paciente, "documento_profesional": usuario["documento"], "fecha": fecha, "tipo": tipo, "descripcion": descripcion}

            try:
                respuestaHttp = requests.post("http://10.128.0.8:8000/agregarAdenda/", json=informacion_adenda)

                if respuestaHttp.status_code == 200:

                    adenda = respuestaHttp.json().get("adenda")

                    if adenda == None:
                        contexto["mensaje"] = "El paciente no existe/El paciente no le pertenece"
                    else:
                        contexto["mensaje"] = "Adenda agregada con exito"
                else:
                    contexto["mensaje"] = "Error en la solicitud al servidor de usuarios"
                
            except requests.exceptions.RequestException as e:
                contexto["mensaje"] = "Error de conexión con el servidor de usuarios"

        return render(request, "pagina_agregar_adenda.html", contexto)

    else:

        if usuario["tipo"] == "profesionalSalud":
            return render(request, "pagina_agregar_adenda.html", usuario)
        else:
            request.session["mensaje_error"] = f"Error al cargar la pagina ya que el {usuario['documento']} no corresponde a un profesional de salud"

    return redirect(reverse("pagina_error"))
    
class AdendaForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")
    fecha = forms.CharField(label="Fecha")
    tipo = forms.CharField(label="Tipo")
    descripcion = forms.CharField(label="Descripción")