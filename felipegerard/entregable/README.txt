# Exponer el puerto de boot2docker
VBoxManage controlvm boot2docker-vm natpf1 "expose-luigid,tcp,127.0.0.1,8082,,8082"

# Inicializar un contenedor con la imagen
docker run -it --name test -p 8082:8082 -v /Users/Felipe/data-science/arte-mexicano/felipegerard/code/luigi/:/home/itam/ felipegerard/pipeline /bin/bash

# Inicializar el central planner de luigi
luigid --background --port 8082 &

# Correr el proceso
itam-tm-default -d test2 --languages spanish,english --topic-range-lda 3,10,2 --topic-range-lsi 40,81,20 --workers 6

# Se puede ver el avance en el navegador: localhost:8082

