from django.shortcuts import render

def index(request):

    contexto = {
        'titulo': 'Pagina principal'
    }

    return render(request, 'mainapp/index.html', contexto)


