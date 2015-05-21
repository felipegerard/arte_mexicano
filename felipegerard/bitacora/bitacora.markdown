BITÁCORA
=====================================


-------------------------------------
2015-05-13
-------------------------------------

**TO DO:**
1. Conectarse al disco y accesar los datos.
2. Checar que sea ~ 1TB de información (1,000,000 de archivos) y verificar los archivos.
3. Vale la pena mandarlo por mail a Amazon? O mejor parallel y SSH? Vale la pena comprimir antes de mandar?
    + Si por la red, script de carga en paralelo (con prueba en pequeña escala)
    + Si en físico, averiguar cómo mandarlo. Lo regresan?
4. Crear cuenta en AWS de ITAM-DS
5. Calcular costo

* EXTRAS:
    + Checar conferencias a las que podríamos ir con el dinero que sobró.


-------------------------------------
2015-05-13 - 2015-05-15
-------------------------------------

# Jared, Mont, Felipe, Petri

* Intentamos conectarnos al disco con un cable cruzado de Ethernet pero no lo logramos. A lo más lográbamos verlo pero no conectarnos.
* Edwin nos ayudó y contactamos al soporte técnico de Lenovo. Nos recomendaron resetear el disco (que se supone que no borra nada más que configuración), perono lo hicimos. EI nos dijo que no, además. Bajamos un software para conectarnos al disco pero no lo logramos usar con éxito. La app está en el Drive.
* También mandamos un mail a EI. Nos dijeron que con un router, pero como no teníamos fuimos con José Calixto. Nos prestó un router ENORME pero quedamos de verlo el lunes tipo a las 11 para configurarlo y ver si nos logramos conectar.
* Fer nos ayudó y logramos conectarnos al disco usando el cable cruzado y la app, poniendo IP manualmente. Subí las imágenes de la configuración de mi compu al Drive. Checar si le debemos las 2hrs * $300 = $600 a Fer. El disco estaba muy lento y nos tuvimos que ir, así que no vimos más que la primera capa de archivos.
* Falta corroborar que todos los archivos estén ahí y ver cuánto espacio ocupan los que nos interesan. También hay que montar la carpeta a una ruta local, para poderla accesar como si fuera cualquier otra.
* __IMPORTANTE__: Le dimos permiso a todos los usuarios desde la app, picando el botón _todos_. Pero igual tenían permiso de todo todos los usuarios registrados. Igual mejor hay que revertirlo para que no haya bronca.

-------------------------------------
2015-05-18
-------------------------------------

# Jared, Mont, Felipe

* Accedimos a los datos con el siguiente proceso:
    +) Se debe usar un Linux para acceder a los datos desde la línea de comandos (o al menos es la única manera que pudimos).
    +) Conectar el disco y la computadora al switch (o directamente, aunque con el switch se puede conectar varias).
    +) Cambiar la IP a 192.168.10.*, donde * debe ser distinto a 181, que es la IP del disco. La máscara debe ser 255.255.255.0. El gateway debe ser 0.0.0.0. El DNS y el search domain deben ir vacíos. Si no se tenía esta configuración previamente, hay que apagar y prender la conexión Ethernet para que agarre.
    +) Desde la interfaz gráfica se puede ver en 'Browse Network (lista izquierda) > Work Group > Conaculta > conaculta > digitalizacion'.
    +) Desde la línea de comandos la carpeta se monta automáticamente (y por eso usamos Linux) en el directorio '/var/run/user/1000/gvfs/smb-share:server=conaculta,share=conaculta/digitalizacion'. Desde esta carpeta se pueden ver los datos como si fuera cualquier carpeta del sistema, excepto que es __MUY__ lenta, incluso para hacer `ls` o cosas similares, por lo que hay que tener cuidado al hacer cualquier cosa.
* Pruebas y diagnósticos:
    +) Total de información: ~900 GB
    +) Velocidad de bajada de carpetas usando `cp -r` con un solo proceso en una sola computadora es de aproximadamente 100MB cada 6 minutos, es decir unos 17MB por minuto. A esta velocidad tardaríamos aproximadamente 41 días en bajar toda la información del disco.
    +) También intentamos comprimir las carpetas antes de pasarlas. Una carpeta de 100MB se tarda aproximadamente 10 segundos en comprimirse y descomprimirse. El tiempo de transferencia es ligeramente menor a 6 minutos, pero en realidad el tiempo total es equivalente a hacerlo con todos los archivos por separado.
    +) Usando `parallel` y copiando cada archivo (no carpeta) por separado, con 8 procesos (con 16 da más o menos igual) se tarda aproximadamente 4.5 minutos en 100 MB. Esto representa una mejora de aproximadamente el 30%, pero no es un _game changer_.
    +) Hicimos una prueba como la primera usando un simple `cp -r` pero copiando la información de una computadora del cubo a otra. En este caso se tardó alrededor de 30 segundos en 100 MB, de modo que entre computadoras la transferencia es ~ 10x la del disco.
    +) Para una última prueba, usamos dos computadoras y cada una con tres `cp -r` simples cada una en una terminal distinta, para un total de 6 procesos simultáneos. Pusimos a bajar carpetas de entre 100 y 350 MB. El proceso tomó 40 minutos. En total bajamos 1389 MB, pero como algunos procesos terminaron primero, suponiendo que en 40 minutos pudiéramos bajar digamos 1.5 GB, tomaría 1000/1.5*40 minutos ~ 17 días, que no es viable tampoco.
* TO DO:
    +) Preguntarle a Adolfo si sabe si podemos hacer algo para mejorar el desempeño. Si no, pedirle a EI una mejor fuente de datos o ver qué se puede hacer.
    +) Llorar :(


-------------------------------------
2015-05-20
-------------------------------------

# Jared, Felipe

* Hicimos algunas pruebas con el switch que trajo Petri y en efecto fue más rápido.
* Logramos conectar la Mac con ese switch, pero no la computadora del cubo... Como que a veces se atonta el disco.
* Notamos que al copiar carpetas hay tiempo perdido: cuando va a comenzar con una carpeta nueva, deja de descargar información varios segundos. Parece como si planeara lo que va a hacer, pero no hace nada durante ese tiempo. Esto es usando `cp -r`.
* Qué bueno que ya no usaremos ese disco! \(*v*)/

















