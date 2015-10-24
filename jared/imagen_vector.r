library(jpeg)
library(dplyr)
library(parallel)

col_dim <- expand.grid(r = seq(0,1, by = .1), g = seq(0,1, by = .1), 
                       b = seq(0,1, by = .1))
col_dim$RGB<-paste(col_dim$r,col_dim$g,col_dim$b,sep ="_")

image_vec<-function(path_image){

  imagen<-readJPEG(path_image)
  imagen.2 <- round(imagen,1)
  
  conteo_colores <- data.frame(r = as.vector(imagen.2[,,1]),
                               g = as.vector(imagen.2[,,2]),
                               b = as.vector(imagen.2[,,3]))
  
  conteo_colores.2 <-group_by(conteo_colores,r,g,b)%>%
    summarize(size = n())%>%
    ungroup()
  
  conteo_colores.3 <- left_join(col_dim, conteo_colores.2)%>%
    mutate(log_size = log(size))
  
  imagen_vector <- conteo_colores.3$log_size
  imagen_vector[is.na(imagen_vector)]<-0
  
  imagen_vector
}

args <-commandArgs(trailingOnly = TRUE)

imagenes<-list.files(args[1])
imagenes<-imagenes[grepl(".jpg",imagenes)]
imagenes<-paste(args[1],imagenes,sep="")

cores <- detectCores()
matriz_col<-mclapply(imagenes, image_vec, mc.cores = cores)

matriz_col.2<-unlist(matriz_col)
matriz_col.3<-matrix(matriz_col.2, nrow = length(matriz_col), ncol = 1331, byrow = TRUE)
rownames(matriz_col.3)<- imagenes
matriz_colores <- data.frame(matriz_col.3)
colnames(matriz_colores)<-col_dim$RGB

saveRDS(matriz_colores, file = "matriz_colores.rds")
write.csv(matriz_colores, file = "matriz_colores.csv")