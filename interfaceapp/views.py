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
                    tipo = respuesta.json().get('tipo')

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
    return render(request, 'pagina_principal_profesionalSalud.html', {'documento': documento})

def vista_principal_paciente(request, documento):
    return render(request, 'pagina_principal_paciente.html', {'documento': documento})

def vista_principal_director(request, documento):
    return render(request, 'pagina_principal_director.html', {'documento': documento})


# DEFINICIÓN DE CLASES AUXILIARES

class LoginForm(forms.Form):
    documento = forms.CharField(label="Documento")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)
