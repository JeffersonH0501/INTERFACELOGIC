import requests
from django.shortcuts import render, redirect
from django import forms
from interfaceapp import producer
from interfaceapp import subscriber

def vista_login(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            usuario = form.cleaned_data['usuario']
            clave = form.cleaned_data['clave']
            informacion_usuario = {'usuario': usuario, 'clave': clave}

            print("> usuario: " + usuario + ", clave: " + clave)

            url_autenticacion = 'http://34.36.86.244:80/api/autenticacion/' #URL del balanceador

            try:
                response = requests.post(url_autenticacion, json=informacion_usuario)

                if response.status_code == 200:

                    respuesta = response.json().get('respuesta')

                    if respuesta == "valido":
                        return redirect('principal')
                    
                    elif respuesta == "invalido":
                        mensaje_error = "Usuario/Clave incorrecto"
                        contexto = {'form': form, 'error_message': mensaje_error}
                        return render(request, 'pagina_login_nuevo.html', contexto)
                    
                else:
                    mensaje_error = "Error en la solicitud al servidor de autenticación"
                    contexto = {'form': form, 'error_message': mensaje_error}
                    return render(request, 'pagina_login_nuevo.html', contexto)
                
            except requests.exceptions.RequestException as e:
                mensaje_error = "Error de conexión con el servidor de autenticación"
                contexto = {'form': form, 'error_message': mensaje_error}
                return render(request, 'pagina_login_nuevo.html', contexto)

    return render(request, 'pagina_login_nuevo.html')

"""
def vista_login(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            usuario = form.cleaned_data['usuario']
            clave = form.cleaned_data['clave']

            print("> usuario: " + usuario + ", clave: " + clave)

            producer.enviar_peticion_autenticacion(usuario, clave)
            subscriber.respuesta_autenticacion = ""  # Restablece la respuesta
            subscriber.detener_consumo = False  # Restablece la bandera
            subscriber.recibir_respuesta_autenticacion() 
            response = subscriber.respuesta_autenticacion
            subscriber.detener_consumo = True

            print("> La respuesta de la solicitud es: " + response)

            if response == "VALIDO":
                return redirect('principal')
            elif response == "INVALIDO":
                error_message = "Usuario/Clave incorrecto"
                context = {'form': form, 'error_message': error_message}
                return render(request, 'pagina_login_nuevo.html', context)
                
    else:
        form = LoginForm()

    return render(request, 'pagina_login_nuevo.html')
"""

def vista_principal(request):
    return render(request, 'pagina_principal.html')

class LoginForm(forms.Form):
    usuario = forms.CharField(label="Usuario")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)
