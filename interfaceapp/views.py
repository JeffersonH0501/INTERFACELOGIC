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
            }

            if usuario['tipo'] == 'profesionalSalud':

                request.session['foto'] = usuario['foto']
                request.session['nombre'] = usuario['nombre']
                request.session['documento'] = usuario['documento']
                request.session['edad'] = usuario['edad']
                request.session['telefono'] = usuario['telefono']
                request.session['sexo'] = usuario['sexo']

                return render(request, 'pagina_principal_profesionalSalud.html', usuario)

            else:
                
                mensaje_error = f"Error al cargar la pagina ya que el {documento}  no corresponde a un profesional de salud"
                nueva_url = reverse('pagina_error', args=[mensaje_error])
                return redirect(nueva_url)

        else:
            mensaje_error = f"Error al cargar la página del profesional de salud: {respuestaHttp.status_code}"
            nueva_url = reverse('pagina_error', args=[mensaje_error])
            return redirect(nueva_url)

    except requests.exceptions.RequestException as e:
        mensaje_error = "Error al cargar la pagina del profesional de salud"
        nueva_url = reverse('pagina_error', args=[mensaje_error])
        return redirect(nueva_url)

def vista_principal_paciente(request, documento):
    return render(request, 'pagina_principal_paciente.html', {'documento': documento})

def vista_principal_director(request, documento):
    return render(request, 'pagina_principal_director.html', {'documento': documento})

def vista_error(request, mensaje_error):
    return render(request, 'pagina_error.html', {'error_message': mensaje_error})

def agregar_adenda(request):

    contexto = {}
   
    if request.method == 'POST':

        contexto['foto'] = request.session.get('foto')
        contexto['nombre'] = request.session.get('nombre')
        documento_profesional = request.session.get('documento')
        contexto['documento'] = documento_profesional
        contexto['edad'] = request.session.get('edad')
        contexto['telefono'] = request.session.get('telefono')
        contexto['sexo'] = request.session.get('sexo')

        form = AdendaForm(request.POST)

        if form.is_valid():

            documento_paciente = form.cleaned_data['documento_paciente']
            fecha = form.cleaned_data['fecha']
            tipo = form.cleaned_data['tipo']
            descripcion = form.cleaned_data['descripcion']

            informacion_adenda = {'documento_paciente': documento_paciente, 'documento_profesional': documento_profesional, 'fecha': fecha, 'tipo': tipo, 'descripcion': descripcion}

            print("> documento: " + documento_paciente + ", documento_profesional: " + documento_profesional + ", fecha: " + fecha + ", tipo: " + tipo)

            url_agregar_adenda = 'http://10.128.0.6:8080/agregarAdenda/' #URL del servidor de usuarios

            try:

                respuestaHttp = requests.post(url_agregar_adenda, json=informacion_adenda)

                if respuestaHttp.status_code == 200:

                    adenda = respuestaHttp.json().get('adenda')

                    if adenda == None:
                        print("Adenda No fue agrega con exito al paciente con documento:", documento_paciente)
                        contexto['mensaje'] = "El paciente no existe/El paciente no le pertenece"
                    else:
                        print("Adenda fue agregada con exito al paciente con documento:", documento_paciente)
                        print("Información de la Adenda:", adenda)
                        contexto['mensaje'] = "Adenda agregada con exito"

                else:
                    contexto['mensaje'] = "Error en la solicitud al servidor de usuarios"
                
            except requests.exceptions.RequestException as e:
                contexto['mensaje'] = "Error de conexión con el servidor de usuarios"

        return render(request, 'pagina_principal_profesionalSalud.html', contexto)
    
    else:
        mensaje_error = "Error al agregar la agenda. La peticion no es POST"
        nueva_url = reverse('pagina_error', args=[mensaje_error])
        return redirect(nueva_url)


# DEFINICIÓN DE CLASES AUXILIARES

class LoginForm(forms.Form):
    documento = forms.CharField(label="Documento")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)

class AdendaForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")
    fecha = forms.CharField(label="Fecha")
    tipo = forms.CharField(label="Tipo")
    descripcion = forms.CharField(label="Descripción")
