import jwt
import json
import base64
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from cryptography.fernet import Fernet


def decodificarMensaje(mensaje_cifrado, llave):
    f = Fernet(llave)
    mensaje_json = f.decrypt(mensaje_cifrado).decode()
    mensaje = json.loads(mensaje_json)
    return mensaje

def consultarUsuarioPaciente(request, documento):

    try:
        respuestaHttp = requests.post("http://10.128.0.8:8000/usuario/", json={"documento": documento})

        if respuestaHttp.status_code == 200:

            respuestaJson = respuestaHttp.json()

            usuario = {
                "documento": respuestaJson.get("documento"),
                "foto": respuestaJson.get("foto"),
                "nombre": respuestaJson.get("nombre"),
                "edad": respuestaJson.get("edad"),
                "telefono": respuestaJson.get("telefono"),
                "sexo": respuestaJson.get("sexo")
            }

            request.session["usuario"] = usuario
        else:
            request.session["mensaje_error"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"
        
    except requests.exceptions.RequestException as e:
        request.session["mensaje_error"] = "Error de conexión con el servidor de usuarios"

def base64_a_bytes(mensaje_base64):
    return base64.b64decode(mensaje_base64)

def consultarHistoriaPaciente(request, documento):

    try:
        respuestaHttp = requests.post("http://10.128.0.8:8000/historia_clinica/", json={"documento_paciente": documento})

        if respuestaHttp.status_code == 200:

            respuestaJson = respuestaHttp.json()

            if respuestaJson.get("mensaje") is None:

                llaveJson = respuestaHttp.json().get("llave_codificada")
                historiaJson = respuestaHttp.json().get("mensaje_codificado")
                historiaJson_bytes = base64_a_bytes(historiaJson)

                llave_decodificada = jwt.decode(llaveJson, settings.SECRET_KEY, algorithms=["HS256"])
                llave_decodificada = base64_a_bytes(llave_decodificada.get("llave"))

                historia_decodificada = decodificarMensaje(historiaJson_bytes, llave_decodificada)

                historia = {
                    "diagnosticos": historia_decodificada.get("diagnosticos"),
                    "tratamientos": historia_decodificada.get("tratamientos"),
                    "notas": historia_decodificada.get("notas"),
                    "adendas": []
                }

                for adenda in historia_decodificada.get("adendas"):
                    historia["adendas"].append(adenda)

                request.session["usuario"]["historia_clinica"] = historia
            
            elif respuestaJson.get("mensaje") == "true":
                request.session["mensaje_rojo"] = "Error de autorización el paciente no le pertence"
        else:
            request.session["mensaje_rojo"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"
    
    except requests.exceptions.RequestException as e:
        request.session["mensaje_rojo"] = "Error de conexión con el servidor de usuarios"


def vista_principal_paciente(request):

    token = request.session.get("token")

    if token is not None:

        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        documento = decoded_token.get("documento")
        tipo = decoded_token.get("tipo")

        if tipo == "paciente":
            
            if request.session.get("usuario") is None:
                consultarUsuarioPaciente(request, documento)

            usuario = request.session.get("usuario")

            if usuario is not None:
                return render(request, "pagina_principal_paciente.html", usuario)
        else:
            request.session["mensaje_error"] = f"Error de autorización al cargar la pagina ya que el documento {documento} no corresponde a un paciente"
    else:
        request.session["mensaje_error"] = "Error de autenticanción al cargar la pagina"
        
    return redirect(reverse("pagina_error"))


def vista_historia_clinica(request):

    token = request.session.get("token")

    if token is not None:

        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        documento = decoded_token.get("documento")
        tipo = decoded_token.get("tipo")

        if tipo == "paciente":
            
            consultarHistoriaPaciente(request, documento)

            usuario = request.session.get("usuario")

            if usuario.get("historia_clinica") is not None:
                return render(request, "pagina_historia_clinica.html", usuario)
            else:
                contexto = usuario.copy()
                contexto["mensaje_rojo"] = request.session.get("mensaje_rojo")
                request.session.pop("mensaje_rojo", None)
                return render(request, "pagina_principal_paciente.html", contexto)
        else:
            request.session["mensaje_error"] = f"Error de autorización al cargar la pagina ya que el documento {documento} no corresponde a un paciente"
    else:
        request.session["mensaje_error"] = "Error de autenticanción al cargar la pagina"
    
    return redirect(reverse("pagina_error"))