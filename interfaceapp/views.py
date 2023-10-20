import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

# FUNCIONES DE LAS DIFERENTES VISTAS DE LA APLIACIÓN

def vista_login(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            documento = form.cleaned_data['documento']
            clave = form.cleaned_data['clave']
            informacion_usuario = {'documento': documento, 'clave': clave}

            print("> documento: " + documento + ", clave: " + clave)

            url_autenticacion = 'http://34.36.86.244:80/autenticacion/' #URL del balanceador

            try:
                respuestaHttp = requests.post(url_autenticacion, json=informacion_usuario)

                if respuestaHttp.status_code == 200:

                    respuesta = respuestaHttp.json().get('respuesta')
                    tipo = respuestaHttp.json().get('tipo')

                    print(respuesta, tipo)
                    
                    if respuesta == "valido":

                        if tipo == 'profesionalSalud':
                            nueva_url = reverse('principal_profesionalSalud', args=[documento])

                        elif tipo == 'paciente':
                            nueva_url = reverse('principal_paciente', args=[documento])

                        elif tipo == 'director':
                            nueva_url = reverse('principal_director', args=[documento])

                        return redirect(nueva_url)

                    elif respuesta == "invalido":
                        mensaje_error = "Documento/Clave incorrecto"
                        contexto = {'form': form, 'error_message': mensaje_error}
                        return render(request, 'pagina_login.html', contexto)
                    
                else:
                    mensaje_error = "Error en la solicitud al servidor de autenticación"
                    contexto = {'form': form, 'error_message': mensaje_error}
                    return render(request, 'pagina_login.html', contexto)
                
            except requests.exceptions.RequestException as e:
                mensaje_error = "Error de conexión con el servidor de autenticación"
                contexto = {'form': form, 'error_message': mensaje_error}
                return render(request, 'pagina_login.html', contexto)
            
    else:
        return render(request, 'pagina_login.html')

def vista_principal_profesionalSalud(request, documento):

    url_usuario = 'http://10.128.0.6:8080/usuario/' #URL del servidor de usuarios

    try:

        respuestaHttp = requests.post(url_usuario, json={'documento': documento})

        if respuestaHttp.status_code == 200:

            usuarioJson = respuestaHttp.json()

            usuario = {
                'documento': usuarioJson.get('documento'),
                'clave': usuarioJson.get('clave'),
                'tipo': usuarioJson.get('tipo'),
                'foto': usuarioJson.get('foto'),
                'nombre': usuarioJson.get('nombre'),
                'edad': usuarioJson.get('edad'),
                'telefono': usuarioJson.get('telefono'),
                'sexo': usuarioJson.get('sexo'),
                'correo': usuarioJson.get('correo')
            }

            if usuario['tipo'] == 'profesionalSalud':
                return render(request, 'pagina_principal_profesionalSalud.html', usuario)

            else:
                mensaje_error = f"Error al cargar la pagina ya que el {documento}  no corresponde a un profesional de salud"
                return render(request, 'pagina_error.html', {'error_message': mensaje_error})

        else:
            mensaje_error = f"Error al cargar la página del profesional de salud: {respuestaHttp.status_code}"
            return render(request, 'pagina_error.html', {'error_message': mensaje_error})

    except requests.exceptions.RequestException as e:
        mensaje_error = "Error al cargar la pagina del profesional de salud"
        return render(request, 'pagina_error.html', {'error_message': mensaje_error})

def vista_principal_paciente(request, documento):
    return render(request, 'pagina_principal_paciente.html', {'documento': documento})

def vista_principal_director(request, documento):
    return render(request, 'pagina_principal_director.html', {'documento': documento})


# DEFINICIÓN DE CLASES AUXILIARES

class LoginForm(forms.Form):
    documento = forms.CharField(label="Documento")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)
