import json
import base64
import jwt
import hashlib
import smtplib
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from email.mime.text import MIMEText
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from datetime import datetime

def enviarNotificacionManipulacion():
    send_mail(
        "Intento Manipulación!!",
        "Se ha detectado un intento de manipulación al agregar una adenda",
        "notificacionintegridad@sharklasers.com",
        ["ja.hernandezg1@uniandes.edu.co"],
        fail_silently=False,
    )

def decodificarMensaje(mensaje_cifrado, llave):
    f = Fernet(llave)
    mensaje_json = f.decrypt(mensaje_cifrado).decode()
    mensaje = json.loads(mensaje_json)
    return mensaje

def consultarUsuarioProfesional(request, documento):

    try:
        respuestaHttp = requests.post("http://10.128.0.8:8000/usuario/", json={"documento": documento})
        
        if respuestaHttp.status_code == 200:
            
            usuarioJson = respuestaHttp.json()

            usuario = {
                "documento": usuarioJson.get("documento"),
                "foto": usuarioJson.get("foto"),
                "nombre": usuarioJson.get("nombre"),
                "edad": usuarioJson.get("edad"),
                "telefono": usuarioJson.get("telefono"),
                "sexo": usuarioJson.get("sexo")
            }

            request.session["usuario"] = usuario

        else:
            request.session["mensaje_error"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"

    except requests.exceptions.RequestException as e:
        request.session["mensaje_error"] = "Error de conexión con el servidor de usuarios"


def agregarAdendaPaciente(request, documento_profesional):

    form = AdendaForm(request.POST)

    if form.is_valid():

        documento_paciente = form.cleaned_data["documento_paciente"]
        fecha = datetime.now()
        fecha = fecha.strftime("%d-%m-%Y")
        tipo = form.cleaned_data["tipo"]
        descripcion = form.cleaned_data["descripcion"]

        informacion_adenda = {"documento_paciente": documento_paciente, "documento_profesional": documento_profesional, "fecha": fecha, "tipo": tipo, "descripcion": descripcion}
        
        informacion_firma = json.dumps(informacion_adenda, sort_keys=True)
        firma = hashlib.sha256(informacion_firma.encode()).hexdigest()
        firma_codificada = jwt.encode({"firma":firma}, settings.SECRET_KEY, algorithm="HS256")

        informacion_adenda["firma_jwt"] = firma_codificada

        try:
            respuestaHttp = requests.post("http://10.128.0.8:8000/agregar_adenda/", json=informacion_adenda)

            if respuestaHttp.status_code == 200:

                respuesta = respuestaHttp.json().get("mensaje")

                if respuesta is None:
                    request.session["mensaje_verde"] = "Adenda agregada con exito"
                elif respuesta == "true":
                    request.session["mensaje_rojo"] = "Error de autorización ya que el paciente no le pertenece"
                elif respuesta == "false":
                    request.session["mensaje_rojo"] = "Error al realizar la solicitud ya que el paciente no existe"
                elif respuesta == "manipulado":
                    enviarNotificacionManipulacion()
                    request.session["mensaje_rojo"] = "Error de integridad ya que hubo un intento externo de manipulación de la adenda"
            else:
                request.session["mensaje_rojo"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"
                
        except requests.exceptions.RequestException as e:
            request.session["mensaje_rojo"] = "Error de conexión con el servidor de usuarios"
    else:
        request.session["mensaje_rojo"] = "El form no es valido"

def base64_a_bytes(mensaje_base64):
    return base64.b64decode(mensaje_base64)

def consultarHistoriaPaciente(request, documento_profesional):

    form = DocumentoForm(request.POST)

    if form.is_valid():

        documento_paciente = form.cleaned_data["documento_paciente"]

        try:
            respuestaHttp = requests.post("http://10.128.0.8:8000/usuario/", json={"documento": documento_paciente})

            if respuestaHttp.status_code == 200:

                respuestaJson = respuestaHttp.json()

                if respuestaJson.get("mensaje") is None:

                    paciente = {
                        "documento": respuestaJson.get("documento"),
                        "foto": respuestaJson.get("foto"),
                        "nombre": respuestaJson.get("nombre"),
                        "edad": respuestaJson.get("edad"),
                        "telefono": respuestaJson.get("telefono"),
                        "sexo": respuestaJson.get("sexo")
                    }

                    respuestaHttp = requests.post("http://10.128.0.8:8000/historia_clinica/", json={"documento_paciente": documento_paciente, "documento_profesional": documento_profesional})

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
                            for adenda in historia_decodificada.get("adendas", []):
                                historia["adendas"].append(adenda)
                            
                            request.session["paciente"] = paciente
                            request.session["paciente"]["historia_clinica"] = historia

                        elif respuestaJson.get("mensaje") == "true":
                            request.session["mensaje_rojo"] = "Error de autorización el paciente no le pertence"
                    else:
                        request.session["mensaje_rojo"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"
                else:
                    request.session["mensaje_rojo"] = "Error al cargar la pagina ya que el paciente no existe"
            else:
                request.session["mensaje_rojo"] = f"Error {respuestaHttp.status_code} con el servidor de usuarios"

        except requests.exceptions.RequestException as e:
            request.session["mensaje_rojo"] = "Error de conexión con el servidor de usuarios"
    else:
        request.session["mensaje_rojo"] = "El form no es valido"


def vista_principal_profesionalSalud(request):

    token = request.session.get("token")

    if token is not None:

        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        documento = decoded_token.get("documento")
        tipo = decoded_token.get("tipo")

        if tipo == "profesionalSalud":

            if request.session.get("usuario") is None:
                consultarUsuarioProfesional(request, documento)
            
            usuario = request.session.get("usuario")

            if usuario is not None:
                return render(request, "pagina_principal_profesionalSalud.html", usuario)
        else:
            request.session["mensaje_error"] = f"Error de autorización al cargar la pagina ya que el documento {documento} no corresponde a un profesional de salud"
    else:
        request.session["mensaje_error"] = "Error de autenticanción al cargar la pagina"
    
    return redirect(reverse("pagina_error"))


def vista_agregar_adenda(request):

    token = request.session.get("token")

    if token is not None:

        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        documento = decoded_token.get("documento")
        tipo = decoded_token.get("tipo")

        if tipo == "profesionalSalud":

            usuario = request.session.get("usuario")

            if request.method == "POST":

                agregarAdendaPaciente(request, documento)

                contexto = usuario.copy()
                contexto["mensaje_verde"] = request.session.get("mensaje_verde")
                contexto["mensaje_rojo"] = request.session.get("mensaje_rojo")

                request.session.pop("mensaje_verde", None)
                request.session.pop("mensaje_rojo", None)

                return render(request, "pagina_agregar_adenda.html", contexto)

            else:
                return render(request, "pagina_agregar_adenda.html", usuario)
        else:
            request.session["mensaje_error"] = f"Error de autorización al cargar la pagina ya que el documento {documento} no corresponde a un profesional de salud"
    else:
        request.session["mensaje_error"] = "Error de autenticanción al cargar la pagina"
    
    return redirect(reverse("pagina_error"))


def vista_consultar_historia(request):

    token = request.session.get("token")

    if token is not None:

        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        documento = decoded_token.get("documento")
        tipo = decoded_token.get("tipo")

        if tipo == "profesionalSalud":

            usuario = request.session.get("usuario")

            if request.method == "POST":

                consultarHistoriaPaciente(request, documento)

                paciente = request.session.get("paciente")
                contexto = usuario.copy()

                if paciente is not None:
                    contexto["paciente"] = paciente
                    request.session.pop("paciente", None)
                    return render(request, "pagina_consultar_historia.html", contexto)
                
                else:
                    contexto["mensaje_rojo"] = request.session.get("mensaje_rojo")
                    request.session.pop("mensaje_rojo", None)
                    return render(request, "pagina_consultar_historia.html", contexto)
            else:
                return render(request, "pagina_consultar_historia.html", usuario)
        else:
            request.session["mensaje_error"] = f"Error de autorización al cargar la pagina ya que el documento {documento} no corresponde a un profesional de salud"       
    else:
        request.session["mensaje_error"] = "Error de autenticanción al cargar la pagina"

    return redirect(reverse("pagina_error"))
     

class AdendaForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")
    tipo = forms.CharField(label="Tipo")
    descripcion = forms.CharField(label="Descripción")

class DocumentoForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")

enviarNotificacionManipulacion()