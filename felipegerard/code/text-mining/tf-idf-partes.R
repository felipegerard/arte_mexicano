library(dplyr)
library(tm)
library(Rstem)
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

# Limpieza
clean_corpus <- function(corp,
                         stem = FALSE,
                         remove_stopwords = TRUE,
                         null_text = 'TEXTOBASURA',
                         mc.cores = 4,
                         lang = NULL,
                         allowed_languages = c('spanish','english',
                                               'french','german',
                                               'portugese')){
  corp <- tm_map(mc.cores = mc.cores,
                 corp,  
                 function(x){
                   meta <- x$meta
                   x <- gsub('\\f', '', x$content)
                   x <- paste0(x, collapse = ' ')
                   x <- gsub('[0-9]{1,3}', '', x)
                   x <- tolower(x)
                   x <- gsub('[^ a-záéíóúüñ0-9]', '', x)
                   x <- gsub(' +', ' ', x)
                   if(is.null(lang)) lang <- textcat(x)
                   #cat(lang)
                   lang_cond <- !is.na(lang) && (lang %in% allowed_languages)
                   if(lang_cond && remove_stopwords){
                     x <- removeWords(x, stopwords(lang))
                   }
                   if(lang_cond && stem){
                     x <- strsplit(x, " ")[[1]]
                     x <- wordStem(x, language=lang)
                     x <- paste(x, collapse=" ")
                   }
                   x <- gsub(' +', ' ', x)
                   if(nchar(x) < 3 || !grepl('[^ ]{2}', x)) x <- null_text
                   #list(content=x, meta=meta)
                   PlainTextDocument(x = x,
                                     author = meta$author,
                                     datetimestamp = meta$datetimestamp,
                                     description = meta$description,
                                     heading = meta$heading,
                                     id = meta$id,
                                     language = ifelse(lang_cond, lang, ''),
                                     origin = meta$origin)
                 })
  corp
  #Corpus(VectorSource(corp))
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
allowed_languages <- c('spanish','english',
                       'french','german',
                       'portugese')

# Mineria -----------------------------------------------------------------

## OJO: Falta detectar el lenguaje para quitar stopwords!!!!

#dir <- DirSource(directory = 'code/text-mining/test/full')
# dir <- DirSource(directory = 'code/text-mining/test-by-page',
#                  pattern = '[0-9]{5}.txt',
#                  recursive = T)
system.time({
  pages <- list.files('data/txt/', # 'code/text-mining/test-by-page', #'code/pdftotext/txt/', #
                      pattern = '[0-9]{5}.txt',
                      full.names = T,
                      recursive = T) %>%
    grep(pattern = '/full/', invert = T, value = T)
})

#pages <- pages[1:10000]
block_size <- 20000

nblocks <- floor(length(pages)/block_size)
idx <- floor(seq(1, length(pages), length.out = nblocks + 1))
times <- character(nblocks)
for(i in 1:(length(idx)-1)){
  now <- as.character(Sys.time())
  print(paste0(i, ' started at ', now))
  times[i] <- now
  ini <- idx[i] + as.numeric(i != 1)
  fin <- idx[i+1]
  pages1 <- pages[ini:fin]
  dir1 <- URISource(pages1)
  corp_1 <- VCorpus(dir1, readerControl = list(reader=readPlain))
  meta(corp_1, 'origin', type='local') <- gsub('.*/([^/]+)/txt/[^/]+', '\\1', pages1)
  corp_clean_aux <- clean_corpus(corp_1,
                                 mc.cores = 6,
                                 stem = FALSE,
                                 remove_stopwords = TRUE,
                                 allowed_languages = allowed_languages)
  tdm_aux <- TermDocumentMatrix(corp_clean_aux,
                                control=list(wordLengths = c(min_wordlength, Inf),
                                             weighting = function(x)
                                               weightSMART(x, spec='ntc')))
  save(tdm_aux, file = paste0('data/temp/tdm/tdm_',i,'.Rdata'))
  save(corp_clean_aux, file = paste0('data/temp/corp/corp_clean_',i,'.Rdata'))
  #     eval(parse(text = paste0('tdm_',i,' <- tdm_aux')))
  #     eval(parse(text = paste0('save(tdm_',i,', file = "data/temp/tdm_',i,'")')))
  #     eval(parse(text = paste0('rm(tdm_',i,')')))
}

for(i in 1:nblocks){
  print(i)
  load(paste0('data/temp/corp/corp_clean_',i,'.Rdata'))
  tdm_aux <- TermDocumentMatrix(corp_clean_aux,
                                control=list(wordLengths = c(min_wordlength, Inf),
                                             weighting = function(x)
                                               weightSMART(x, spec='ntc')))
  save(tdm_aux, file = paste0('data/temp/tdm/tdm_',i,'.Rdata'))
}

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
