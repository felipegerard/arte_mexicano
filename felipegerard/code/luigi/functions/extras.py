# coding=utf-8
import os

def obtener_rutas(rutaBase, extension='.pdf'):
    return [os.path.join(rutaBase,x) for x in os.listdir(rutaBase) if extension in x]