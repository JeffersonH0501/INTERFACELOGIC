from django.shortcuts import render, redirect
from django import forms
from .. import producer
from .. import subscriber

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

            respuesta = subscriber.recibir_respuesta_autenticacion()

            print(respuesta)
            if respuesta is not None:
                return redirect('index.thml')  
    
    else:
        form = LoginForm()

    return render(request, 'pagina_principal.html', {'form': form})

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
