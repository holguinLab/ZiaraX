from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request,'panel/login.html')

def index(request):
    return render(request,'index.html')

def formularios(request):
    return render(request,'formularios.html')

def data_tables(request):
    return render(request,'data-tables.html')


def servicio_barba(request):
    return render(request,'servicios/servicio_barba.html')

def servicio_corte(request):
    return render(request,'servicios/servicio_corte.html')


def servicio_spa(request):
    return render(request,'servicios/servicio_spa.html')


def producto_aceite(request):
    return render(request,'productos/producto_aceite.html')

def producto_crema(request):
    return render(request,'productos/producto_crema.html')

def producto_locion(request):
    return render(request,'productos/producto_locion.html')

def admin_panel(request):
    return render(request,'admin_panel.html')

def carrito(request):
    return render(request,'carrito.html')