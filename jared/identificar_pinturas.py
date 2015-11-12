from scipy import misc
from joblib import Parallel, delayed  
import multiprocessing
import csv

def rgb2gray(rgb):
    """
    Convertir imagenes en escala de grises
    """
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

def ident_print(linea):
    pagina = misc.imread(linea[0:len(linea)-1])
    pagina = rgb2gray(pagina)
    if pagina.var()>5000:
        return linea[0:len(linea)-1]

archivos = []

imagen_dir = open("todos_jpg.txt")

for line in imagen_dir:
    archivos.append(line)
imagen_dir.close()


#Checo en paralelo que paginas tienen imagenes 
num_cores = multiprocessing.cpu_count()
resultado = Parallel(n_jobs=num_cores)(delayed(ident_print)(i) for i in archivos)
resultado = filter(None,resultado)

csvfile = "imagenes.csv"

with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in resultado:
        writer.writerow([val])
