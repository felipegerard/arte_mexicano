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


clean_corpus <- function(corp, mc.cores = 4){
  corp <- mclapply(mc.cores = mc.cores,
                   corp,
                   function(x){
    x <- gsub('\\f', '', x)
    x <- paste0(x, collapse = ' ')
    x <- gsub('[0-9]{1,3}', '', x)
    x <- tolower(x)
    x <- gsub('[^ a-záéíóúüñ0-9]', '', x)
    x <- gsub(' +', ' ', x)
    x <- removeWords(x, stopwords('spanish'))
  })
  cat('Terminada fase 1')
  corp <- mclapply(mc.cores = mc.cores,
                   corp,
                   function(x){
                      z <- strsplit(x, " ")[[1]]
                      z <- wordStem(z, language="spanish")
                      z <- paste(z, collapse=" ")
                      z <- gsub(' +', ' ', z)
                   })
  Corpus(VectorSource(corp))
}


# Mineria -----------------------------------------------------------------

## OJO: Falta detectar el lenguaje para quitar stopwords!!!!

dir <- DirSource(directory = 'code/text-mining/test/full')
corp_1 <- VCorpus(dir, readerControl = list(readPlain))[1:10]
corp_1
docnames <- sapply(corp_1, function(x) meta(x)$id)
data.frame(docnames, lang=textcat(corp_1)) # No detecta tan bien...
corp_clean <- clean_corpus(corp_1, mc.cores = 8)
tdm_1 <- TermDocumentMatrix(corp_clean,
                            control=list(wordLengths = c(2, Inf),
                                         weighting = function(x)
                                           weightSMART(x, spec='ntc')))
dictionary_1 <- tdm_1$dimnames$Terms
mat_1 <- sparseMatrix(i=tdm_1$i, j=tdm_1$j, x=tdm_1$v)
tdm_1$dimnames$Docs

# Ejemplo
as.character(corp_clean[[8]])
query  <- 'ésta es la historia de un vitral filosófico que resplandecía y se identificaba con el sol. Para colmo, la luz incandescente lo quemaba y no tenía ni un mínimo de paz'

#limpieza del query
query_clean <- Corpus(VectorSource(query))
query_clean <- clean_corpus(query_clean)
query_vec_1 <- TermDocumentMatrix(query_clean, 
                                  control = list(dictionary = dictionary_1,
                                                 wordLengths=c(1, Inf))) 

query_vec_2 <- as.matrix(query_vec_1)/sqrt(sum(query_vec_1^2)) #normalizar con ntc el query
scores <- as.numeric(t(mat_1)%*%query_vec_2)

out <- data.frame(id=docnames,
                  score=scores) %>%
  arrange(desc(score))
out


