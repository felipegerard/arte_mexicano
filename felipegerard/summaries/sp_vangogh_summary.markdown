Image Processing for Artist Identification. Computerized Analysis of Vincent van Gogh's Painting Brushtrokes
=============================================================

Se analiza un conjunto de 101 imágenes de alta resolución de pinturas de Van Gogh (vG), mezcladas con algunas falsas. El objetivo es describir el estilo de vG para comprenderlo mejor y para poder identificar los cuadros genuinos de las copias o del trabajo de otros pintores. Tres universidades distintas trabajaron en el proyecto por separado:

* __Pennsylvania:__ Textura (_wavelets_ D4 + 2D Hidden Markov Model (HMM)) y contornos (clustering, distancia de Mallows).
* __Princeton:__ Estilo (wavelets complejos + HMM) y fluidez (medianas).
* __Maastricht:__ Textura (_wavelets_ de Gabor).

Todos los equipos decidieron partir las pinturas en un mosaico para su análisis, aunque no necesariamente usaron piezas del mismo tamaño.

Pennsylvania
---------------------

__Variables:__

    1. Coeficientes de la transformada wavelet a diferentes escalas para la textura.
    2. Características de la geometría de los trazos, como longitud, orientación y curvatura de los contornos, que son obtenidas con un algoritmo de detección de bordes.

__Modelos:__

    1. HMM: Generan un HMM para cada uno de los grupos de variables, pero no explican para qué los usan...
    2. K-Medias: Utilizan K-Medias para hacer una especie de histograma de las imágenes, pero tampoco explican mucho...
    3. Para sacar la similitud entre dos pinturas (o entre una pintura y una colección de pinturas), tomaron un cuadrado de la imagen 1 y calcularon la distancia al cuadrado más cercano de la imagen 2. Luego repitieron el proceso con el segundo más parecido, etc.

__Resultados:__

Entrenaron el modelo con 23 de las imágenes que se sabe que son auténticas y luego calcularon la distancia de las 76 restantes al conjunto de entrenamiento. La idea era entonces que las más lejanas deberían ser falsas y las más cercanas deberían ser auténticas. Los resultados fueron razonables pero no excelentes.

Princeton
-----------------------

__Variables:__

Se tomaron los coeficientes de los wavelets a diversas resoluciones y se modeló el hecho de pertenecer o no a un borde mediante un Hidden Markov Tree (un HMM especial) de dos estados ocultos.

__Modelo:__

Se numeran las variables por su poder discriminante y se toman $m$. Se utilizó una distancia cuadrática _boosteada_ por la efectividad de las variables, únicamente tomando las $m$ primeras. Luego se escalaron las variables con un "algoritmo de escalamiento multidimensional" y se proyectaron a 3 dimensiones. Las pinturas falsas tienden a estar más lejos del centroide, así que se usó un clasificador de radio (si están más lejos del centroide son falsas y si están más cerca son auténticas).

__Resultados:__

Los resultados del modelo fueron aceptables pero no definitivos. Analizando en la escala más chica se dieron cuenta de que los _wavelets_ en las escalas más finas tienen más peso en las copias por la falta de fluidez del trazo a la hora de copiar.

Maastricht
-----------------------

__Variables:__

Utilizando los coeficientes de los _wavelets_ de Gabor se obtuvo la "energía" para cada combinación de 4 escalas y 6 orientaciones, para un total de 24 variables.

__Modelo:__

De manera simplista se puede utilizar la energía total (suma de las energías) para identificar las copias porque (como concluyó el grupo de Princeton) tienden a tener bordes más marcados.

Por otro lado, utilizaron las 24 variables como entradas para una SVM con validación cruzada. Dado que se hace por parches, se toma la moda de la predicción de los parches de una imagen para clasificarla.

__Resultados:__

En este caso los resultados también fueron moderadamente buenos, pero no definitivos.
