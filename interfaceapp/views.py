from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def pagina_principal(request):
    return render(request, 'pagina_principal.html')
