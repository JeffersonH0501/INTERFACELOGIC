import jwt
from django.conf import settings
import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from cryptography.fernet import Fernet

cipher_suite = Fernet(settings.SIMETRIC_KEY.encode())

def descifrar_dato(dato):
    return cipher_suite.decrypt(dato).decode()

def vista_login(request):

    if request.method == "POST":

        form = LoginForm(request.POST)
        mensaje_error = ""

        if form.is_valid():

            documento = form.cleaned_data["documento"]
            clave = form.cleaned_data["clave"]
            informacion_usuario = {"documento": documento, "clave": clave}

            try:
                respuestaHttp = requests.post("http://34.36.86.244:80/autenticacion/", json=informacion_usuario)

                if respuestaHttp.status_code == 200:

                    token = respuestaHttp.json().get("token")
                    
                    if token is not None:
                         
                        request.session["token"] = token

                        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                        tipo = descifrar_dato(decoded_token.get("tipo"))

                        print(tipo)
                        print(decoded_token)

                        if tipo == "paciente":
                            nueva_url = reverse("paciente")
                        elif tipo == "profesionalSalud":
                            nueva_url = reverse("profesionalSalud")
                        elif tipo == "director":
                            nueva_url = reverse("director")

                        return redirect(nueva_url)

                    else:
                        mensaje_error = "Documento/Clave incorrecto"
                else:
                    mensaje_error = f"Error {respuestaHttp.status_code} en la solicitud al servidor de autenticación"
                
            except requests.exceptions.RequestException as e:
                mensaje_error = "Error de conexión con el servidor de autenticación"
            
        return render(request, "pagina_login.html", {"error_message": mensaje_error})
    
    return render(request, "pagina_login.html")
    
def vista_error(request):
    mensaje_error = request.session.get("mensaje_error")
    request.session.pop("mensaje_error", None)
    return render(request, "pagina_error.html", {"error_message": mensaje_error})

class LoginForm(forms.Form):
    documento = forms.CharField(label="Documento")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)


