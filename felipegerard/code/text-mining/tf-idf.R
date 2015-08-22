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
                         mc.cores = 4,
                         allowed_languages = c('spanish','english',
                                               'french','german',
                                               'portugese')){
  corp <- tm_map(#mc.cores = mc.cores,
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
                     if(lang_cond){
                       x <- removeWords(x, stopwords(lang))
                     }
                     x <- strsplit(x, " ")[[1]]
                     if(lang_cond){
                       x <- wordStem(x, language=lang)
                     }
                     x <- paste(x, collapse=" ")
                     x <- gsub(' +', ' ', x)
                     if(nchar(x) < 3 || !grepl('[^ ]{2}', x)) x <- 'TEXTOBASURA'
                     #list(content=x, meta=meta)
                     PlainTextDocument(x = x, author = meta$author, datetimestamp = meta$datetimestamp, description = meta$description, heading = meta$heading, id = meta$id, language = ifelse(lang_cond, lang, ''), origin = meta$origin)
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
dir <- DirSource(directory = 'code/text-mining/test-by-page',
                 pattern = '[0-9]{5}.txt',
                 recursive = T)
corp_1 <- VCorpus(dir, readerControl = list(readPlain))
corp_clean <- clean_corpus(corp_1, mc.cores = 6, allowed_languages = allowed_languages)

corp_clean
corp_clean[[2]]$meta
corp_clean[[2]]$content

docnames <- sapply(corp_clean, function(x) meta(x)$id)
languages <- mclapply(mc.cores = 6,
                      corp_clean,
                      function(x) textcat(x$content)) %>%
  unlist
meta <- data.frame(id=docnames, lang=languages) # No detecta tan bien...

tdm_1 <- TermDocumentMatrix(corp_clean,
                            control=list(wordLengths = c(min_wordlength, Inf),
                                         weighting = function(x)
                                           weightSMART(x, spec='ntc')))
dictionary_1 <- tdm_1$dimnames$Terms
mat_1 <- sparseMatrix(i=tdm_1$i, j=tdm_1$j, x=tdm_1$v)
tdm_1$dimnames$Docs # Igual a docnames: identical(tdm_1$dimnames$Docs, y = docnames)


# Ejemplo -----------------------------------------------------------------

#as.character(corp_clean[[8]])
query  <- 'la transformación del alma es un momento de mucha filosofía y reencuentro'
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
  arrange(desc(lang == query_lang), lang, desc(score)) ### Hay que pensar esto mejor

# Resultados
out %>% head(10)
ver <- out$id[2]
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






