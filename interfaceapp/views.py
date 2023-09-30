from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth import authenticate, login

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirige a la página de inicio o a donde desees
                return redirect('index.thml')  # Reemplaza 'nombre_de_la_vista' por el nombre de tu vista principal
    
    else:
        form = LoginForm()

    return render(request, 'pagina_principal.html', {'form': form})

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
