from django.shortcuts import render, redirect
from django import forms
from django.template import RequestContext
from interfaceapp import producer
from interfaceapp import subscriber

def vista_login(request):

    if request.method == 'POST':

        print(request)
        form = LoginForm(request.POST)

        print(form)
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
                error_message = "Credenciales de inicio de sesión incorrectas. Por favor, inténtelo de nuevo."
                context = {'form': form, 'error_message': error_message}
                return render(request, 'pagina_login.html', context)
                
    else:
        form = LoginForm()

    return render(request, 'pagina_login.html')

def vista_principal(request):
    return render(request, 'pagina_principal.html')

class LoginForm(forms.Form):
    usuario = forms.CharField(label="Usuario")
    clave = forms.CharField(label="Clave", widget=forms.PasswordInput)
