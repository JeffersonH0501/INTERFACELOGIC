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

            print(username, password)
            producer.enviar_peticion_autenticacion(username, password)
            subscriber.recibir_respuesta_autenticacion() 

            response = subscriber.respuesta_autenticacion

            if response == "VALIDO":
                return render(request, 'pagina_principal.html', {'form': form})
    else:
        form = LoginForm()
    
    return render(request, 'index.html', {'form': form})

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
