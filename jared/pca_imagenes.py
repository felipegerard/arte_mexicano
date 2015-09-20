import os
from scipy import misc
import numpy as np
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans

def rgb2gray(rgb):
    """
    Convertir imagenes en escala de grises
    """
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

imagenes = [os.path.join("pinturas/jpgs_reducidos",x) for x 
    in os.listdir("pinturas/jpgs_reducidos")]

def image_vec(pagina):
    pagina = misc.imread(pagina)
    pagina_2 = rgb2gray(pagina)
    return pagina_2.reshape(1,60000)

mat_pin = [image_vec(pagina)[0] for pagina in imagenes]
mat_pin = np.array(mat_pin)/256
mat_pin = mat_pin.round()
mat_pin = csr_matrix(mat_pin)

svd = TruncatedSVD(n_components=5, random_state=42)

X = svd.fit_transform(mat_pin) 

print(svd.explained_variance_ratio_)
print(svd.explained_variance_ratio_.sum())

km = KMeans(n_clusters=5, init='k-means++', max_iter=100, n_init=1)

km.fit(X)

for i in range(5):
    newpath = "pinturas/jpgs_reducidos/cluster_" + str(i)
    if not os.path.exists(newpath): os.makedirs(newpath)

imag = os.listdir("pinturas/jpgs_reducidos")
for i in range(len(imagenes)):
    os.rename(imagenes[i], "pinturas/jpgs_reducidos/cluster_" + str(km.labels_[i]) + "/" + str(imag[i]))


