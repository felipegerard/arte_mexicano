library(lsa)
library(parallel)

matriz_colores <- readRDS("matriz_colores.rds")

cores <- detectCores()

set.seed(2705)
#Se crean 300 funciones hash, en las se multiplica por un 
#vector aletorio
f.hash.lista <- mclapply(1:300, function(i){
  v <- rnorm(1331)
  function(x){
    ifelse(sum(v*x) >= 0, 1, -1) 
  }
}, mc.cores = cores)

#Se crea una matriz similar a minhash
mat.firmas <- apply(matriz_colores, 1, function(x){sapply(f.hash.lista, function(f) f(x))})

#Se crean las bandas
mat.firmas.split <- split(data.frame(mat.firmas), rep(1:5, each = 60))

bitsToInt <-function(z) {
  ## podemos usar el siguiente código
  sum((2^seq(0, length(z)-1, 1))*z)
}

cubetas <- mclapply(mat.firmas.split, function(df){
  apply(df, 2, function(x){ bitsToInt(as.numeric(x>0))  })
}, mc.cores = cores)

lista.pares <- mclapply(cubetas, function(cub){
  tab.1 <- table(cub)
  nombres.1 <- names(tab.1)[tab.1>=2]
  hashes.1 <- lapply(nombres.1, function(i){ which(cub == i)})
  lapply(hashes.1, function(x) combn(x, 2))  ## ordenados.
}, mc.cores = cores)

pares <- t(Reduce('cbind',Reduce('c',lista.pares)))

pares.2 <- unique(data.frame(pares))

sims.1<-mclapply(1:nrow(pares.2), function(i){
  index.1 <- pares.2[i,1]
  index.2 <- pares.2[i,2]
  similitud <- as.numeric(cosine(as.numeric(matriz_colores[index.1,]),
                    as.numeric(matriz_colores[index.2,])))
  c(similitud, rownames(matriz_colores[index.1,]),rownames(matriz_colores[index.2,]))
}, mc.cores = cores)

similitudes <- Reduce("rbind",sims.1)

saveRDS(similitudes, file = "similitudes_paginas.rds")
write.csv(similitudes, file = "similitudes_paginas.csv")