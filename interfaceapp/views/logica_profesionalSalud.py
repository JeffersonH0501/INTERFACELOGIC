import json
import jwt
import hashlib
import smtplib
from email.mime.text import MIMEText
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode

def enviarNotificacionManipulacion():
    try:
        servidor_correo = smtplib.SMTP('tu_servidor_smtp', tu_puerto_smtp)
        servidor_correo.starttls()
        servidor_correo.login('tu_correo@gmail.com', 'tu_contraseña')

        mensaje = MIMEText("Se ha detectado un intento de manipulación en la adenda.")
        mensaje['Subject'] = 'Alerta de Manipulación de Adenda'
        mensaje['From'] = 'tu_correo@gmail.com'
        mensaje['To'] = 'correo_del_admin@tu_empresa.com'

        servidor_correo.sendmail('tu_correo@gmail.com', ['correo_del_admin@tu_empresa.com'], mensaje.as_string())
        
        servidor_correo.quit()

    except Exception as e:print(f"Error al enviar la notificación: {str(e)}")


def decodificarMensaje(mensaje_codificado, llave):

    ciphertext = urlsafe_b64decode(mensaje_codificado.encode())

    backend = default_backend()
    cipher = Cipher(algorithms.AES(llave), modes.CFB, backend=backend)
    decryptor = cipher.decryptor()

    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_message.decode()


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

        informacion_adenda["firma"] = firma

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

                    respuestaHttp = request.post("http://10.128.0.8:8000/historia_clinica/", json={"documento_paciente": documento_paciente, "documento_profesional": documento_profesional})

                    if respuestaHttp.status_code == 200:
                        
                        respuestaJson = respuestaHttp.json()

                        if respuestaJson.get("mensaje") is None:

                            llaveJson = respuestaHttp.json().get("llave_codificada")
                            historiaJson = respuestaHttp.json().get("historia_codificada")

                            llave_decodificada = jwt.decode(llaveJson, settings.SECRET_KEY, algorithms=["HS256"])
                            historia_decodificada = decodificarMensaje(historiaJson, llave_decodificada)

                            historia = {
                                "diagnosticos": historia_decodificada.get("diagnosticos"),
                                "tratamientos": historia_decodificada.get("tratamientos"),
                                "notas": historia_decodificada.get("notas"),
                                "adendas": []
                            }
                            for adenda in historia_decodificada.get("adendas"):
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
                consultarUsuarioProfesional(request)
            
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
    fecha = forms.CharField(label="Fecha")
    tipo = forms.CharField(label="Tipo")
    descripcion = forms.CharField(label="Descripción")

class DocumentoForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")