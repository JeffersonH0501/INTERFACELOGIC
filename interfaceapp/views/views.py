import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

def agregar_adenda(request):

    contexto = {}
   
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

        url_agregar_adenda = 'http://10.128.0.8:8000/agregarAdenda/' #URL de kong

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

    return contexto

def vista_login(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)
        mensaje_error = ""

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
                            request.session['documento'] = documento
                            nueva_url = reverse('vista_agregar_adenda')

                        elif tipo == 'paciente':
                            nueva_url = reverse('principal_paciente', args=[documento])

                        elif tipo == 'director':
                            nueva_url = reverse('principal_director', args=[documento])

                        return redirect(nueva_url)

                    elif respuesta == "invalido":
                        mensaje_error = "Documento/Clave incorrecto"
                    
                else:
                    mensaje_error = "Error en la solicitud al servidor de autenticación"
                
            except requests.exceptions.RequestException as e:

                mensaje_error = "Error de conexión con el servidor de autenticación"
            
        return render(request, 'pagina_login.html', {'error_message': mensaje_error} )
            
    else:
        return render(request, 'pagina_login.html')
    
def vista_agregar_adenda(request):

    if request.method == 'POST':
        contexto = agregar_adenda(request)
        return render(request, 'pagina_agregar_adenda.html', contexto)

    else:

        documento = request.session.get('documento')
        url_usuario = 'http://10.128.0.8:8000/usuario/' #URL de kong

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
                    request.session['edad'] = usuario['edad']
                    request.session['telefono'] = usuario['telefono']
                    request.session['sexo'] = usuario['sexo']

                    print("entro")
                    return render(request, 'pagina_agregar_adenda.html', usuario)

                else:
                    request.session['mensaje_error'] = f"Error al cargar la pagina ya que el {documento}  no corresponde a un profesional de salud"

            else:
                request.session['mensaje_error'] = f"Error ({respuestaHttp.status_code}) al cargar la página del profesional de salud"

        except requests.exceptions.RequestException as e:
            request.session['mensaje_error'] = "Error al cargar la pagina del profesional de salud"
        
        return redirect(reverse('pagina_error'))
    
def vista_principal_paciente(request, documento):

    url_usuario = 'http://10.128.0.8:8000/usuario/' #URL de kong

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
                'historia_clinica': {
                    'diagnosticos': usuarioJson.get('historia_clinica').get('diagnosticos'),
                    'tratamientos': usuarioJson.get('historia_clinica').get('tratamientos'),
                    'notas': usuarioJson.get('historia_clinica').get('notas')
                },
                'adendas': []
            }

            for adenda in usuarioJson.get('adendas'):
                usuario['adendas'].append(adenda)

            request.session['paciente'] = usuario

            if usuario['tipo'] == 'paciente':
                print("entro")
                return render(request, 'pagina_principal_paciente.html', usuario)

            else:
                request.session['mensaje_error'] = f"Error al cargar la pagina ya que el {documento}  no corresponde a un paciente"

        else:
            request.session['mensaje_error'] = f"Error ({respuestaHttp.status_code}) al cargar la página del paciente"

    except requests.exceptions.RequestException as e:
        request.session['mensaje_error'] = "Error al cargar la pagina del paciente"
        
    return redirect(reverse('pagina_error'))

def vista_principal_director(request, documento):

    url_usuario = 'http://10.128.0.8:8000/usuario/' #URL de kong

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

            if usuario['tipo'] == 'director':
                return render(request, 'pagina_principal_director.html', usuario)

            else:
                request.session['mensaje_error'] = f"Error al cargar la pagina ya que el {documento}  no corresponde a un director"

        else:
            request.session['mensaje_error'] = f"Error ({respuestaHttp.status_code}) al cargar la página del director"

    except requests.exceptions.RequestException as e:
        request.session['mensaje_error'] = "Error al cargar la pagina del director"
        
    return redirect(reverse('pagina_error'))

def vista_historiaClinica_paciente(request, documento):

    usuario = request.session.get('paciente')

    print(usuario)

    if usuario['tipo'] == 'paciente':
        return render(request, 'pagina_historia_clinica.html', usuario)
    
    else:
        request.session['mensaje_error'] = f"Error al cargar la pagina ya que el {usuario['documento']}  no corresponde a un paciente"
    
    return redirect(reverse('pagina_error'))

def vista_error(request):
    mensaje_error = request.session.get('mensaje_error')
    return render(request, 'pagina_error.html', {'error_message': mensaje_error})

class LoginForm(forms.Form):
    documento = forms.CharField(label="Documento")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)

class AdendaForm(forms.Form):
    documento_paciente = forms.CharField(label="Documento Paciente")
    fecha = forms.CharField(label="Fecha")
    tipo = forms.CharField(label="Tipo")
    descripcion = forms.CharField(label="Descripción")
