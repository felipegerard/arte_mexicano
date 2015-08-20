library(dplyr)
library(tm)
library(Rstem)

# dat <- read.table(file = 'code/text-mining/txt/bow-full/bow_reduced.psv', header = F, sep = '|', quote = "", col.names = c('book','term','count'), colClasses = c('numeric','character','numeric'))
# dim(dat)
# head(dat)


# Funciones ---------------------------------------------------------------


clean_corpus <- function(corp){
  corp <- tm_map(corp, function(x){
    x <- gsub('\\f', '', x)
    x <- paste0(x, collapse = ' ')
    x <- gsub('[0-9]{1,3}', '', x)
    x <- tolower(x)
    x <- gsub('[^ a-záéíóúüñ0-9]', '', x)
    x <- gsub(' +', ' ', x)
    x <- removeWords(x, stopwords('spanish'))
  })
  corp <- tm_map(corp,function(x){
    z <- strsplit(x, " ")[[1]]
    z <- wordStem(z, language="spanish")
    z <- paste(z, collapse=" ")
    z <- gsub(' +', ' ', z)
    PlainTextDocument(z)
  })
}


# Mineria -----------------------------------------------------------------


dir <- DirSource(directory = 'code/text-mining/test/full')
corp_1 <- VCorpus(dir, readerControl = list(readPlain))
corp_test <- corp_1[1:10]

clean_corpus(corp_test)[[1]]


clean_corpus <- function(corp){
  corp <- tm_map(corp,function(x){
    x <- gsub('[0-9]{1,3}', '', x)
    x <- gsub('[-]|<br>',' ',x)
    x <- gsub('[^ a-zA-ZáéíóúüÁÉÍÓÚÜñÑ0-9]', '', x)
    gsub('( .)+ ', ' ', x)
  })
  corp <- tm_map(corp,removeWords,stopwords("spanish"))
  corp <- tm_map(corp, function(x) stripWhitespace(x) %>% tolower)
  corp <- tm_map(corp,function(x){
    z <- strsplit(x, " ")[[1]]
    z.stem <- wordStem(z, language="spanish")
    PlainTextDocument(paste(z.stem, collapse=" "))
  })
  
  text_clean <- sapply(corp, function(x) x[[1]])
  is_empty <- text_clean == ''
  text_clean <- text_clean[!is_empty]
  list(corpus=Corpus(VectorSource(text_clean)), empty=is_empty)
}


list.1 <- clean_corpus(Corpus(VectorSource(art$text)))






