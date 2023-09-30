from django.shortcuts import render, redirect
from django import forms
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
    else:
        form = LoginForm()
    
    pass

def entrar():
    return render('pagina_principal.html')

def no_entrar():
    return render('index.html')

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
