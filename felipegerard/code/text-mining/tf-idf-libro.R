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

# Limpiar textos (libros)
clean_book_corpus <- function(dirs, mc.cores = 4){
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



# Calcular scores
analyze <- function(query, # String con el texto
                    query_lang = NULL,
                    matriz, # TDM convertida a matriz
                    dict, # Diccionario obtenido de la TDM
                    meta, # Matriz con los metadatos del corpus
                    min_wordlength = 2)
{
  #limpieza del query
#   query <- 'frida kahlo'
#   query_lang <- 'spanish'
#   matriz <- mat
#   dict <- dictionary
#   meta <- meta
#   min_wordlength <- min_wordlength
  
  query_clean <- VectorSource(query)
  query_clean <- clean_book_corpus(query_clean)
  if(!is.null(query_lang)) query_clean[[1]]$meta$language <- query_lang
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
  
  out <- cbind(meta, score=scores) %>%
    filter(score != 0) %>%
    arrange(desc(score))
  list(info = out,
       query = query,
       query_clean = query_clean,
       query_vec = query_vec_2)
}

# Mostrar resultados
print_results <- function(out, txt_path, idx, print_matching_lines = FALSE)
{
#   out <- info
#   txt_path <- 'data/full-txt/'
#   idx <- 1
  
  dat <- out$info[idx,]
  id <- dat$id %>% as.character
  lang <- dat$lang %>% as.character
  score <- dat$score %>% as.numeric
  txt <- VCorpus(URISource(paste(path, id, sep = '/')))[[1]]$content
  cat(c('\n------------------------',
        'Datos generales',
        '------------------------',
        paste('Libro:  ', id),
        paste('Idioma: ', lang),
        paste('Score:  ', round(score, 3))),
      sep = '\n')
  # El query como realmente se usó después de procesarlo
  cat(c('\n------------------------',
        'Palabras clave',
        '------------------------\n'),
      sep = '\n')
  q <- out$query_clean[[1]]$content
  q <- sort(strsplit(q, ' ')[[1]])
  cat(paste(q, collapse=', '))
  cat('\n')
  
  # Las palabras relevantes para el match
  cat(c('\n------------------------',
        'Palabras relevantes',
        '------------------------\n'),
      sep = '\n')
  relevant <- mat[,id] * out$query_vec
  notzero <- (relevant > 0)
  relevant <- data.frame(word = rownames(relevant)[notzero],
                         score_contrib = as.numeric(relevant[,1])[notzero])
  print(relevant)
  
  # Las líneas que hicieron match
  if(print_matching_lines){
    cat(c('\n------------------------',
          'Líneas que coincidieron',
          '------------------------\n'),
        sep = '\n')
    query_grep <- out$query_clean[[1]]$content %>%
      gsub(pattern = '^ ', replacement = '') %>%
      gsub(pattern = ' ', replacement = '|')
    matches <- grep(query_grep, txt, value = F, ignore.case = T)
    matches <- paste(matches, txt[matches], sep = ': ')
    cat(matches, sep = '\n')
  }
}

# Control -----------------------------------------------------------------

min_wordlength <- 2
max_wordlength <- 25
min_docs <- 2
allowed_languages <- c('spanish','english',
                       'french','german',
                       'portuguese', 'italian')


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
path <- 'data/full-txt'
dirs <- list.files(path, full.names = T)
dirs <- dirs[!(dirs %in% paste0(path, '/',blacklist))]


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
  corp_partial <- clean_book_corpus(URISource(dirs1), mc.cores = 4)  
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
save(corp, file = 'data/corpora/corpus_books_sinfiltrar.Rdata')

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

### De frecuencias sin stemming para LDA
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

### Con stemming

load('data/corpora/corpus_books_completo_stem.Rdata')

# TF para análisis exploratorio
tdm_tf_stem <- TermDocumentMatrix(corp_stem,
                                  control = list(
                                    weighting = weightTf,
                                    bounds = list(global = c(min_docs, Inf)),
                                    wordLengths = c(min_wordlength, max_wordlength)
                                  ))
tdm_tf_stem
save(tdm_tf_stem, file = 'data/tdms/tdm_books_tf_stem.Rdata')

# TF-IDF
tdm_tfidf_stem <- TermDocumentMatrix(corp_stem,
                                     control = list(
                                       weighting = weightTfIdf,
                                       bounds = list(global = c(min_docs, Inf)),
                                       wordLengths = c(min_wordlength, max_wordlength)
                                     ))

tdm_tfidf_stem
save(tdm_tfidf_stem, file = 'data/tdms/tdm_books_tfidf_stem.Rdata')

# log(TF)-IDF para que haga match con más palabras
tdm_logtfidf_stem <- weightSMART(tdm_tf_stem, spec = 'ltc')

tdm_logtfidf_stem
save(tdm_logtfidf_stem, file = 'data/tdms/tdm_books_logtfidf_stem.Rdata')



# i <- 4
# nchar(corp2[[i]])
# textcat(corp2[[i]])
# a <- removeWords(corp2[[i]], stopwords(textcat(corp2[[i]])))


# Ejemplo queries ---------------------------------------------------------

system.time({
  docnames <- meta(corp_stem, 'id', type='local') %>% unlist
  languages <- meta(corp_stem, 'language', type='local') %>% unlist
  meta <- data.frame(id=docnames,
                     lang=languages) # No detecta tan bien... Poner moda por libro?
  
  dictionary <- tdm_logtfidf_stem$dimnames$Terms
  dims <- tdm_logtfidf_stem$dimnames
  dims$Docs <- gsub('list\\("(.+)"\\)', '\\1', dims$Docs)
  mat <- sparseMatrix(i=tdm_logtfidf_stem$i,
                      j=tdm_logtfidf_stem$j,
                      x=tdm_logtfidf_stem$v,
                      dimnames = dims)
})

save(mat, dictionary, meta, file = 'docs/app-tfidf/data/basics.Rdata')

query <- 'pinturas murales de david alfaro siqueiros'
query <- 'african art'

info <- analyze(query, query_lang = NULL, matriz = mat, dict = dictionary, meta = meta, min_wordlength = min_wordlength)
head(info$info)  
print_results(info, 'data/full-txt/', idx = 1)
print_results(info, 'data/full-txt/', idx = 2)
print_results(info, 'data/full-txt/', idx = 3)
print_results(info, 'data/full-txt/', idx = 4)









