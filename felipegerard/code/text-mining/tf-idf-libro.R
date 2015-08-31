library(dplyr)
library(tm)
# library(Rstem)
library(parallel)
library(Matrix)
library(textcat)

# dat <- read.table(file = 'code/text-mining/txt/bow-full/bow_reduced.psv', header = F, sep = '|', quote = "", col.names = c('book','term','count'), colClasses = c('numeric','character','numeric'))
# dim(dat)
# head(dat)


# Funciones ---------------------------------------------------------------

# Uso de memoria
lh <- function(l){
  options(scipen=999)
  data.frame(
    object = l,
    mb = round((sapply(l, function(x) pryr::object_size(eval(parse(text = x)))))/2^20, 2)
  )
}

# Calculo de scores
analyze <- function(query, # String con el texto
                    matriz, # TDM convertida a matriz
                    dict, # Diccionario obtenido de la TDM
                    meta, # Matriz con los metadatos del corpus
                    min_wordlength = 2,
                    lang = NULL)
{
  #limpieza del query
  query_clean <- Corpus(VectorSource(query))
  query_clean <- clean_corpus(query_clean,
                              stem = FALSE,
                              remove_stopwords = TRUE,
                              lang = lang)
  query_vec_1 <- TermDocumentMatrix(query_clean, 
                                    control = list(dictionary = dict,
                                                   wordLengths=c(min_wordlength, Inf))) 
  norm_1 <- sqrt(sum(query_vec_1^2))
  if(norm_1 == 0){
    query_vec_2 <- query_vec_1 %>% as.matrix # Puros ceros
  } else {
    query_vec_2 <- as.matrix(query_vec_1)/norm_1 #normalizar con ntc el query
  }
  scores <- as.numeric(t(matriz)%*%query_vec_2)
  
  out <- data.frame(id=docnames,
                    score=scores) %>%
    filter(score != 0) %>%
    left_join(meta) %>%
    arrange(desc(score))
  list(info = out,
       query = query,
       query_clean = query_clean,
       query_vec = query_vec_2)
}

# Mostrar resultados
print_results <- function(out, corp, mat, idx)
{
  info <- out$info[idx,]
  cat(c('\n------------------------',
        'Datos generales',
        '------------------------',
        paste('Libro:  ', as.character(info$origin)),
        paste('Archivo:', as.character(info$id)),
        paste('Idioma: ', as.character(info$lang)),
        paste('Score:  ', round(info$score, 3))),
      sep = '\n')
  ver <- out$info$id[idx] %>% as.character
  # La página tal cual
  cat(c('\n------------------------',
        'Texto original',
        '------------------------\n'),
      sep = '\n')
  content <- tm_filter(corp, FUN = function(x) x$meta$id == ver)[[1]]$content %>%
    gsub(pattern = '\\f', replacement = '\\\\f')
  cat(content, sep = '\n')
  # El query como realmente se usó después de procesarlo
  cat(c('\n------------------------',
        'Palabras clave',
        '------------------------\n'),
      sep = '\n')
  q <- out$query_clean[[1]]$content
  q <- sort(strsplit(q, ' ')[[1]])
  cat(paste(q, collapse=', '))
  cat('\n')
  # Las líneas que hicieron match
  cat(c('\n------------------------',
        'Líneas que coincidieron',
        '------------------------\n'),
      sep = '\n')
  query_grep <- out$query_clean[[1]]$content %>%
    gsub(pattern = '^ ', replacement = '') %>%
    gsub(pattern = ' ', replacement = '|')
  cat(grep(query_grep, content, value = T, ignore.case = T), sep = '\n')
  # Las palabras relevantes para el match
  cat(c('\n------------------------',
        'Plabras relevantes',
        '------------------------\n'),
      sep = '\n')
  relevant <- mat[,ver] * out$query_vec
  notzero <- (relevant > 0)
  relevant <- data.frame(word = rownames(relevant)[notzero],
                         score_contrib = as.numeric(relevant[,1])[notzero])
  print(relevant)
}

# Control -----------------------------------------------------------------

min_wordlength <- 2
max_wordlength <- 25
min_docs <- 2
allowed_languages <- c('spanish','english',
                       'french','german',
                       'portuguese', 'italian')





# Limpiar textos (libros)

clean_book_corpus <- function(dirs, mc.cores = 4){
  dirs <- URISource(dirs)
  corp <- VCorpus(dirs, readerControl = list(reader=readPlain))
  ids <- meta(corp, 'id', type='local')
  corp <- tm_map(corp, mc.cores = mc.cores, function(x) paste(x, collapse=' '))
#   corp <- tm_map(corp, mc.cores = mc.cores, removePunctuation)
  corp <- tm_map(corp, mc.cores = mc.cores, gsub,
                 pattern='\\f|[0-9]{1,3}| . ', replacement=' ')
  corp <- tm_map(corp, mc.cores = mc.cores, tolower)
  corp <- tm_map(corp, mc.cores = mc.cores, gsub,
                 pattern = '[^ 0-9a-záéíóúäëïöüñ]', replacement = '')
  corp <- tm_map(corp, mc.cores = mc.cores, function(x){
    lang <- textcat(x)
    return(PlainTextDocument(x, language = lang))
  })
  corp <- tm_map(corp, mc.cores = mc.cores, stripWhitespace)
  
  meta(corp, 'id', type='local') <- ids
  corp
}



# Mineria -----------------------------------------------------------------

## OJO: Falta detectar el lenguaje para quitar stopwords!!!!

blacklist <- c('concordantiae.txt',
               'universidad_mensual_de_cultura_popular_nov_1936_n.10_t.2.txt',
               'mockobcknnkpemab.txt',
               'theatre_des_martyrs.txt',
               'cien_dibujos_de_diego_rivera.txt',
               'rincones_de_mexico.txt',
               'elementos_de_composicion_musical.txt',
               'enciclopedia_metodica_estampas__tomo_1.txt',
               'la_historia_danzante_tomo_ii_mexico_1874.txt',
               'baron_van_munch-hausen.txt'
               )

# Lista de archivos - lista negra
dirs <- list.files('data/full-txt', full.names = T) %>%
  grep(pattern = blacklist, invert = T, value = T)

block_size <- 30

nblocks <- floor(length(dirs)/block_size)
idx <- floor(seq(1, length(dirs), length.out = nblocks + 1))
times <- character(nblocks)
for(i in 1:(length(idx)-1)){
  now <- as.character(Sys.time())
  print(paste0(i, ' started at ', now))
  times[i] <- now
  ini <- idx[i] + as.numeric(i != 1)
  fin <- idx[i+1]
  dirs1 <- dirs[ini:fin]
  uri1 <- URISource(dirs1)
  corp_partial <- clean_book_corpus(uri1, mc.cores = 4)  
  save(corp_partial, file = paste0('data/temp/corp-book/corp_book_',i,'.Rdata'))
  rm(corp_partial)
  gc()
}

# Pegamos los corpus chicos
load('data/temp/corp-book/corp_book_1.Rdata')
corp <- corp_partial
for(i in 2:nblocks){
  print(i)
  load(paste0('data/temp/corp-book/corp_book_',i,'.Rdata'))
  corp <- c(corp, corp_partial)
}

# Quitamos los documentos con lenguajes no permitidos
corp <- tm_filter(corp, function(x, langs){
  meta(x)$language %in% langs
}, langs=allowed_languages)

# Salvamos el corpus
corp
save(corp, file = 'data/corpora/corpus_books_completo.Rdata')

# Corpus + stemming
corp_stem <- tm_map(corp, function(x, allowed_languages){
  meta <- meta(x)
  if(meta$language %in% allowed_languages){ # Redundante pero por seguridad
    x <- stemDocument(x, language = meta$language)
#     x <- removeWords(x, words = stopwords(meta$language))
  }
  return(x)
}, allowed_languages=allowed_languages)

save(corp_stem, file = 'data/corpora/corpus_books_completo_stem.Rdata')


# TDM ---------------------------------------------------------------------

# De frecuencias sin stemming para LDA
load('data/corpora/corpus_books_completo.Rdata')
tdm_tf_nostem <- TermDocumentMatrix(corp,
                                    control = list(
                                      weighting = weightTf,
                                      bounds = list(global = c(min_docs, Inf)),
                                      wordLengths = c(min_wordlength, max_wordlength)
                                    ))
tdm_tf_nostem
save(tdm_tf_nostem, file = 'data/tdms/tdm_books_tf_nostem.Rdata')

rm(corp, tdm_tf_nostem, tdm_tfidf_nostem)
gc()

# Con stemming

load('data/corpora/corpus_books_completo_stemming.Rdata')

tdm_tf_stem <- TermDocumentMatrix(corp_stem,
                                  control = list(
                                    weighting = weightTf,
                                    bounds = list(global = c(min_docs, Inf)),
                                    wordLengths = c(min_wordlength, max_wordlength)
                                  ))
tdm_tf_stem
save(tdm_tf_stem, file = 'data/tdms/tdm_books_tf_stem.Rdata')

tdm_tfidf_stem <- TermDocumentMatrix(corp_stem,
                                     control = list(
                                       weighting = weightTfIdf,
                                       bounds = list(global = c(min_docs, Inf)),
                                       wordLengths = c(min_wordlength, max_wordlength)
                                     ))

tdm_tfidf_stem
save(tdm_tfidf_stem, file = 'data/tdms/tdm_books_tfidf_stem.Rdata')



# i <- 4
# nchar(corp2[[i]])
# textcat(corp2[[i]])
# a <- removeWords(corp2[[i]], stopwords(textcat(corp2[[i]])))


  
  










# No borrar ---------------------------------------------------------------


load('data/temp/tdm/tdm_1.Rdata')
tdm <- tdm_aux
for(i in 2:nblocks){
  print(i)
  load(paste0('data/temp/tdm/tdm_',i,'.Rdata'))
  tdm <- c(tdm, tdm_aux)
}
tdm
save(tdm, file = 'data/processed_data/tdm_completa.Rdata')

load('data/temp/corp/corp_clean_1.Rdata')
corp <- corp_clean_aux
for(i in 2:nblocks){
  print(i)
  load(paste0('data/temp/corp/corp_clean_',i,'.Rdata'))
  corp <- c(corp, corp_clean_aux)
}
corp
save(corp, file = 'data/processed_data/corpus_completo.Rdata')



# Para los primeros 321 libros (~ 600 MB) con 6 procesos se tarda 427 segs en cargar los datos, 1058 segs en limpiarlos y 124 segs en generar la matriz de metadatos, la TDM, etc.

corp_clean
corp_clean[[2]]$meta
corp_clean[[2]]$content


which(as.numeric(as.matrix(tdm['lruftusemittunten',])) > 0)
which(as.numeric(as.matrix(tdm['pefuá',])) > 0)
idx
load('data/temp/corp/corp_clean_4.Rdata')
62221-60926
corp_clean_aux[[1295]]$content
corp_clean_aux[[1295]]$meta

system.time({
  docnames <- sapply(corp_clean, function(x) meta(x)$id)
  books <- sapply(corp_clean, function(x) meta(x)$origin)
  # languages <- mclapply(mc.cores = 6,
  #                       corp_clean,
  #                       function(x) textcat(x$content)) %>%
  #   unlist
  languages <- sapply(corp_clean, function(x) meta(x)$language)
  meta <- data.frame(origin=books,
                     id=docnames,
                     lang=languages) # No detecta tan bien... Poner moda por libro?
  
  tdm_1 <- TermDocumentMatrix(corp_clean,
                              control=list(wordLengths = c(min_wordlength, Inf),
                                           weighting = function(x)
                                             weightSMART(x, spec='ntc')))
  dictionary_1 <- tdm_1$dimnames$Terms
  mat_1 <- sparseMatrix(i=tdm_1$i, j=tdm_1$j, x=tdm_1$v, dimnames = tdm_1$dimnames)
})
