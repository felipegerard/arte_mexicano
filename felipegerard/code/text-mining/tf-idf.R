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

clean_corpus <- function(corp,
                         stem = FALSE,
                         remove_stopwords = TRUE,
                         null_text = 'TEXTOBASURA',
                         mc.cores = 4,
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
                   lang <- textcat(x)
                   cat(lang)
                   lang_cond <- !is.na(lang) && (lang %in% allowed_languages)
                   if(lang_cond && remove_stopwords){
                     x <- removeWords(x, stopwords(lang))
                   }
                   if(lang_cond){
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
pages <- list.files('code/text-mining/test-by-page', #'code/pdftotext/txt/', #
                    pattern = '[0-9]{5}.txt',
                    full.names = T,
                    recursive = T) %>%
  grep(pattern = '/full/', invert = T, value = T)

dir <- URISource(pages)
corp_1 <- VCorpus(dir, readerControl = list(reader=readPlain))
# Agregamos los nombres de los libros a los metadatos
# Asumimos que la estructura es <ruta a libros>/libro/txt/archivo.txt
for(i in 1:length(corp_1)){
  corp_1[[i]]$meta$origin <- gsub('.*/([^/]+)/txt/[^/]+', '\\1', pages[i])
}
system.time({
  corp_clean <- clean_corpus(corp_1,
                             mc.cores = 6,
                             stem = FALSE,
                             remove_stopwords = TRUE,
                             allowed_languages = allowed_languages)
})

# Para los primeros 75 libros con 6 procesos se tarda como 110 segs

corp_clean
corp_clean[[2]]$meta
corp_clean[[2]]$content

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
tdm_1$dimnames$Docs # Igual a docnames: identical(tdm_1$dimnames$Docs, y = docnames)


# Ejemplo -----------------------------------------------------------------

#as.character(corp_clean[[8]])
query  <- 'african primitive art Gauguin expression'
#query <- corp_1[[999]]$content %>% paste(collapse=' ')
query <- 'Hidalgo'
query_lang <- textcat(query)

#limpieza del query
query_clean <- Corpus(VectorSource(query))
query_clean <- clean_corpus(query_clean)
query_vec_1 <- TermDocumentMatrix(query_clean, 
                                  control = list(dictionary = dictionary_1,
                                                 wordLengths=c(min_wordlength, Inf))) 
norm_1 <- sqrt(sum(query_vec_1^2))
if(norm_1 == 0){
  query_vec_2 <- query_vec_1 %>% as.matrix # Puros ceros
} else {
  query_vec_2 <- as.matrix(query_vec_1)/norm_1 #normalizar con ntc el query
}
scores <- as.numeric(t(mat_1)%*%query_vec_2)

out <- data.frame(id=docnames,
                  score=scores) %>%
  filter(score != 0) %>%
  left_join(meta) %>%
  arrange(desc(score))
  #arrange(desc(lang == query_lang), lang, desc(score)) ### Hay que pensar esto mejor

# Resultados
out %>% head(10)
ver <- out$id[2] %>% as.character
content <- tm_filter(corp_1, FUN = function(x) x$meta$id == ver)[[1]]$content
# La página tal cual
content
# El query como realmente se usó después de procesarlo
query_clean[[1]]$content
# Las líneas que hicieron match
query_grep <- query_clean[[1]]$content %>%
  gsub(pattern = '^ ', replacement = '') %>%
  gsub(pattern = ' ', replacement = '|')
grep(query_grep, content, value = T, ignore.case = T)
# Las palabras relevantes para el match
relevant <- mat_1[,ver] * query_vec_2
relevant[relevant > 0,]




