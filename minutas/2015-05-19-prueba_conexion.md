
# Pruebas de conexión al disco (@carpetri)

Me estoy conectando al disco por el Finder super trivial, lo concecté con mi router que no es Gigabit así que toda esta prueba está limitada a esa velocidad de tranferencia. Asigné el ip del router para que tenga ip 192.168.10.1. el router asigna ips automático, el de mi compu fue el 134 en este caso. El del disco se quedó fijo en el el 181. Para montarlo en en finder entré con la clave de usuario que nos dieron:

-	Usuario: userc1
-	Contraseña:	XXXX

La carperta que debemos subir a Amazón del disco es 

	`/mnt/pools/A/A0/Conaculta/digitalizacion`

Para conectarme desde el Finder sólo abres 	Go/Connect to Server en la dirección smb://192.168.10.181. El Finder por default se conecta directo a `/mnt/pools/A/A0/Conaculta`

## Observaciones

- Lo primero que se hizo fue checar cuánto pesa en realidad lo que necesitamos subir. 
Para pesarlo `du -sh /Volumes/Conaculta/digitalizacion` este comando tarda bastante. no lo esperé, felipe dice que son 900gb


- Lo primero que salta es que los nombres de los arcvhivos no están estandarizados como lo indica el documento del Drive. Puede ser que valga la pena esperar a que los estandarizen ellos para poder subirlos a Amazon para no tener que repetir el proceso ya que esté todo arriba (SUPONIENDO QUE LO HICIERON BIEN Y SE PUEDE REPLICAR)

## Prueba 1. Copia local.

### Primer intento
	
Por pura curiosidad, copié el folder 'encuentro' de 169 mb tardó 3 min en copiarse a mi compu.

Es un libro de poesía que tiene 162 páginas más la portada y contra portada; es decir, 164 jpegs y 164 pdfs suman los 169mb. En promedio cada archivo (página) cerca de 500 kb.

### Segundo intento

Aleatoriamente copíe ahora la carpeta `UN SIGLO DE ARTE MEXICANO 1900-2000` resultó estar vacía!!!!!
 	- Malditos.

En pocas palabras tendremos que estar preparados para que esté lo más desordenado posible.


### Tercer intento

Aleatoriamente copíe ahora la carpeta `UN BELGE AU MEXIQUE` también vacía.


### Tercer intento

Aleatoriamente copíe ahora la carpeta `UN RESCATE DE LA FANTASIA EL ARTE DE LOS LAGARTO SIGLO XVI Y XVII` también vacía.


### Cuarto intento

Intenté copiar 'ZUÑIGA' pra probar qué pasa con el encoding. Parece que será también un problema.

Tuve que hacerlo así

`time cp -rf /Volumes/Conaculta/digitalizacion/ZUN<0303>IGA ~/Desktop/digitalizacion`

Se tardó 4min, 25 seg. con 264mb

Es un libro de Arte  que tiene 157 páginas más la portada y contra portada; es decir, 159 jpegs y 159 pdfs suman los 264mb. En promedio cada archivo (página) pesa  como 800 kb.


## Prueba 2. Copia en paralello

Generé primero libreria.txt con un ls.  Corrí en parallelo, tengo 4 cores.

`time head libreria.txt | parallel 'cp -rf  /Volumes/Conaculta/digitalizacion/{} ~/Desktop/digitalizacion/'`

las carpetas fueron

  - 101_masterpieces_of_american_primative_painting
  - 1200 YEARS OF ITALIAN SCULPTURE
  - 12_artistas_donde_se_origina_el_arte_en_el_aire
  - 12_dibujos_de_jose_maria_velasco
  - 20_dibujos_mexicanos_de_maroto
  - 25 ESTUDIOS DE FOLKLORE
  - 300_anos_de_fraudes_en_el_comercio_de_antiguedades
  - 330_grabados_originales_manuel_manilla
  - 45_contemporary_mexican_artists
  - 50 años de danza en el Palacio de Bellas Artes 1934 - 1984 Vol. 2

Fueron 4.7 gb y trardaron 38 minutos







## Upload al s3 con el la red de mi casa.

Primero, lo cargue con s3cmd  aquí están las instrucciones que usé para instalar. 
AGUAS Q ESTE ARCHIVO INCLUYE LAS LLAVES DE ACCESO DEL AWS PARA EL S3.


``` brew install s3cmd
==> Downloading https://homebrew.bintray.com/bottles/s3cmd-1.5.2.yosemite.bottle
######################################################################## 100.0%
==> Pouring s3cmd-1.5.2.yosemite.bottle.tar.gz
🍺  /usr/local/Cellar/s3cmd/1.5.2: 54 files, 840K
➜  ~  s3cmd --configure 

Enter new values or accept defaults in brackets with Enter.
Refer to user manual for detailed description of all options.

Access key and Secret key are your identifiers for Amazon S3. Leave them empty for using the env variables.
Access Key: AKIAJPGQLTRHEQLICCGA
Secret Key: dCxAJfnIPUAushEKrjh0LxRtnSXtK7oqgPrP0Lh4
Default Region [US]: Oregon

Encryption password is used to protect your files from reading
by unauthorized persons while in transfer to S3
Encryption password: arte
Path to GPG program: 

When using secure HTTPS protocol all communication with Amazon S3
servers is protected from 3rd party eavesdropping. This method is
slower than plain HTTP, and can only be proxied with Python 2.7 or newer
Use HTTPS protocol [No]: No

On some networks all internet access must go through a HTTP proxy.
Try setting it here if you can't connect to S3 directly
HTTP Proxy server name: 

New settings:
  Access Key: XXXXXXXXXXXX
  Secret Key: XXXXXXXXXXXX
  Default Region: Oregon
  Encryption password: arte
  Path to GPG program: None
  Use HTTPS protocol: False
  HTTP Proxy server name: 
  HTTP Proxy server port: 0

Test access with supplied credentials? [Y/n] Y
Please wait, attempting to list all buckets...
Success. Your access key and secret key worked fine :-)

Now verifying that encryption works...
Not configured. Never mind.

Save settings? [y/N] y
Configuration saved to '/Users/Carlos/.s3cfg'
```

Para cargar los archivos usé 

`s3cmd -q -r put CARPETA_A_SUBIR s3://einformativa/digitalizacion/`

1.  La carpeta que subí fue la primera `101_masterpieces_of_american_primative_painting`, de 213 mb. Tarda como un segundo por archivo, son como 164*2 (pdf y jpg) archivos.

12.19s user 5.77s system 3% cpu 8:07.84 total`


2. La carpeta que subí (en este caso con el internet del ITAM SANTA TERESA WIFI itammovil2) fue  `12_artistas_donde_se_origina_el_arte_en_el_aire`, de 270 mb. Tarda como un segundo por archivo, son como 240*2 (pdf y jpg) archivos, o 240 segundos, como 11 minutos.

`6.61s user 2.96s system 1% cpu 10:39.91 total`


## El último paso 

Lo ultimo que se debe intentar es subir sin copiar. Es decir montar el disco y subir desde alguna compu sin copiar al disco de la compu. No debería se muy distino. 

Esto no lo probe porque no pude configurar el router para que me diera internet en el ITAM conservando los ips para poder conectarme al disco.

Habrá que checar cómo hacer esto.




