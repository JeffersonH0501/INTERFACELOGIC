from django.shortcuts import render, redirect
from django import forms
from django.template import RequestContext
from interfaceapp import producer
from interfaceapp import subscriber

def index(request):
    return render(request, 'index.html')

def login_view(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print("> usuario: "+username+", clave: "+password)

            producer.enviar_peticion_autenticacion(username, password)
            subscriber.respuesta_autenticacion = ""  # Restablece la respuesta
            subscriber.detener_consumo = False  # Restablece la bandera
            subscriber.recibir_respuesta_autenticacion() 
            response = subscriber.respuesta_autenticacion
            subscriber.detener_consumo = True

            print("> La respuesta de la solicitud es: "+response)

            if response == "VALIDO":
                # Redirige a la página principal si la respuesta es "VALIDO"
                return redirect('pagina_principal')
    else:
        form = LoginForm()
        
    return render(request, 'index.html')

def pagina_principal(request):
    # Lógica para la vista de la página principal
    return render(request, 'pagina_principal.html')

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
