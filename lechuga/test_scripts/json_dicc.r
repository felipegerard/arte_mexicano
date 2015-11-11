library(jsonlite)
validation_data <- fromJSON("/Users/lechuga/Dropbox/Andres/Escuela/ESCUELA/ITAM/CONAYCT/LDA_python/arte_mexicano_antiguo/lechuga/luigi/test/results/document_results_stopwords_spanish_30.json", flatten=TRUE)

#############################################

library(rjson)
json_file <- "/Users/lechuga/Dropbox/Andres/Escuela/ESCUELA/ITAM/CONAYCT/LDA_python/arte_mexicano_antiguo/lechuga/luigi/test/results/document_results_stopwords_spanish_30.json"
json_data <- fromJSON(file=json_file)
json_file <- lapply(json_data, function(x) {
  x[sapply(x, is.null)] <- NA
  unlist(x)
})
a <- as.data.frame(do.call("rbind", json_file))



asFrame <- do.call("rbind.fill", lapply(json_data, as.data.frame))


#############################################

l <- fromJSON(file=json_file)
l[[26]]$libros[[1]][3]
m <- lapply(
  l[[1]]$libros, 
  function(x) c(x$libros[[1]][1], x$libros[[1]][2], x[[1]][3])
)

m <- do.call(rbind, m)

#############################################