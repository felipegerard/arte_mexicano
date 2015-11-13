
def generarSeccionXML(libro, )

def generarXML(js):
	#self.url = http://200.66.82.41:8080
	url_base = self.url_base
	cadena = "\n\t<libro handle=\"123456789/"+self.consultar(libro)+"\">"
	for nombre,url in listaSimilares:
			nombre = nombre.replace("_"," ")
			nombre = nombre.replace("&","&amp;")
			nombre = nombre.replace("\"","&quot;")
			nombre = nombre.replace("<", "&lt;")
			nombre = nombre.replace(">", "&gt;")
			nombre = nombre.replace("'", "&apos;")
			nombre = nombre.title()
			cadena += "\n\t\t<similar>"
			cadena += "\n\t\t\t<titulo>"+nombre+"</titulo>"
			cadena += "\n\t\t\t<href>"+url_base+"/xmlui/handle/123456789/"+url+"</href>"
			cadena += "\n\t\t</similar>"
	cadena += "\n\t</libro>"
	return cadena