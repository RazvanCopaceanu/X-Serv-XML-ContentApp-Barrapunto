from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import urllib.request

# Create your views here.

from .models import Persona

FORMULARIO = """
<form action="" method="POST">
  Nombre: <input type="text" name="nombre"><br>
  Descripcion: <input type="text" name="descripcion"><br>
  <input type="submit" value="Enviar">
</form>
"""

class myContentHandler(ContentHandler):

    def __init__ (self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""
        self.file = open("contenidos.html", "w")
        self.line = ""

    def startElement (self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True
            
    def endElement (self, name):
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.line = "Titulo de la noticia: " + self.theContent + "."
                # To avoid Unicode trouble
                print (self.line)
                self.file.write(self.line)
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.link = self.theContent
                links = "<p>Enlace noticia: <a href='" + self.link + "'>" + self.link + "</a></p>\n"
                print (links)
                self.file.write(links)
                self.inContent = False
                self.theContent = ""
                self.link = ""

    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars

def barrapunto(request):
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)
    url = "http://barrapunto.com/index.rss"
    xmlStream = urllib.request.urlopen(url)
    theParser.parse(xmlStream)
    return("<p>Enlace fichero: <a href='url'</a></p>")


def barra(request):
    if request.user.is_authenticated():
        logged = 'Logged in as ' + request.user.username + '. <a href="/logout">Logout</a>'
    else:
        logged = 'Not logged in. <a href="/login">Login</a>'
    personas = Persona.objects.all()
    respuesta = "<ul>"
    for persona in personas:
        respuesta += '<li>' + "  " + str(persona.id) + "--->" + persona.nombre + ":  con la siguiente descripcion:   " + persona.descripcion
        respuesta += "</ul>"
    return HttpResponse(logged + "<br>" + respuesta + "<br><br>" + str(barrapunto(request)))


@csrf_exempt
def persona(request, num):
    if request.method == "POST":
        persona = Persona(nombre = request.POST['nombre'], descripcion = request.POST['descripcion'])
        persona.save()
        HttpResponse("La nueva persona es: " + persona.nombre + " con descripcion: " + persona.descripcion)
    try:
        persona = Persona.objects.get(id=int(num))
    except Persona.DoesNotExist:
        return HttpResponse("Esa persona no existe")
    respuesta = "Id: " + str(persona.id) + "<br>"
    respuesta += "Nombre: " + persona.nombre + "<br>"
    respuesta += "Descripcion: " + persona.descripcion
    if request.user.is_authenticated():
        respuesta += "<br><br>" + FORMULARIO
    else:
        respuesta += "<br><br>" + "Se necesita login para introducir persona nueva: <a href='/login/'>Login</a>"
    return HttpResponse(respuesta)

#edit permite editar solo personas guardas en la base de datos. No puede editar personas que no esten en la BD
@csrf_exempt
def edit(request, num):
    if request.method == "POST":
        persona = Persona.objects.get(id=int(num))
        nueva_persona = Persona(id=persona.id, nombre = request.POST["nombre"], descripcion = request.POST["descripcion"]) 
        nueva_persona.save(force_update=True)
        HttpResponse("La nueva persona es: " + nueva_persona.nombre + " con descripcion: " + nueva_persona.descripcion)
    try:
        persona = Persona.objects.get(id=int(num))
    except Persona.DoesNotExist:
        return HttpResponse("La persona " + num +  " no está guardada")
    if request.user.is_authenticated():
        respuesta = 'Logged in as ' + request.user.username + '. <a href="/logout">Logout</a>' + "<br><br>" + FORMULARIO
    else:
        respuesta = 'Not logged in. Necesitas estar autenticado para editar personas <a href="/login">Login</a>'
    return HttpResponse(respuesta)