library(Matrix)
library(dplyr)
library(tm)
library(slam)
library(Rstem)
library(ggplot2)
library(wordcloud)

#install.packages("Rstem", repos = "http://www.omegahat.org/R", type="source")


################################################  lectura de la informacion ###########################################


art <- read.csv('data/processed_data/art_sample.psv', header = F, sep = '|', quote = '')
names(art) <- c('id','doc','text')

################################################ Función auxiliar #######################################################

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
    z <- strsplit(x, " +")[[1]]
    z.stem <- wordStem(z, language="spanish")
    PlainTextDocument(paste(z.stem, collapse=" "))
  })
  
  text_clean <- sapply(corp, function(x) x[[1]])
  is_empty <- text_clean == ''
  text_clean <- text_clean[!is_empty]
  list(corpus=Corpus(VectorSource(text_clean)), empty=is_empty)
}


################################################  Análisis por Título (title) #####################################


# creamos el corpus y limpiamos caracteres especiales del titulo

list.1 <- clean_corpus(Corpus(VectorSource(art$text)))

corp.1 <- list.1$corpus
idx.1 <- list.1$empty

###################  Creacion de la matriz terminos documentos y los pesos por ntc (title)  ############################

#creamos la matriz terminos documentos
tdm.1 <- TermDocumentMatrix(corp.1, control=list(wordLengths=c(2, Inf)))
mat.1 <- sparseMatrix(i=tdm.1$i, j=tdm.1$j, x = tdm.1$v)
dictionary_1 <- tdm.1$dimnames$Terms

tdm.2 <- weightSMART(tdm.1, spec = 'ntc')
mat.2 <- sparseMatrix(i=tdm.2$i, j=tdm.2$j, x = tdm.2$v)

################################################ Multiplicacion query * tdm (title) ############################################

query  <- 'china'

#limpieza del query
query.clean <- Corpus(VectorSource(query))
query.clean <- clean_corpus(query.clean)$corpus
query.vec.1 <- TermDocumentMatrix(query.clean, 
                                  control = list(dictionary = dictionary_1,
                                                 wordLengths=c(1, Inf))) 

query.vec.1 <- as.matrix(query.vec.1)/sqrt(sum(query.vec.1^2)) #normalizar con ntc el query


score_1 <- data.frame(id=which(!list.1$empty),
                      score=as.numeric(t(mat.2)%*%query.vec.1))


out_1 <- art %>%
  left_join(score_1) %>%
  arrange(desc(score))
res_1 <- out_1 %>% head(15)
res_1$text <- gsub('<br>','',res_1$text)

##############################################  histograma de discriminacion ##########################################

m <- data.frame(min=min(res_1$score))
ggplot() +
  geom_bar(data=out_1, mapping=aes(x=score)) +
  geom_vline(data=res_1, aes(xintercept=min(score)), color='red')


##############################################  WordCloud ##########################################

### FALTA HACER ESTO!!
best <- function(nmatch = 3, nterm = 5, alpha=.5){
  vq.1 <- query.vec.1
  vq.abst <- query.vec.abst
  
  outlist <- list()
  
  for(i in 1:nmatch){
    
    v.j.1 <- mat.1[,idx_top_1[i]]
    v.j.abst <- mat.abst[,idx_top_abst[i]]
    
    v1 <- v.j.1*vq.1
    v2 <- v.j.abst*vq.abst
    
    top_contrib_1 <- order(v1,decreasing=T)
    top_contrib_abst <- order(v2,decreasing=T)
    
    df.1 <- data.frame(term=dictionary_1[top_contrib_1[1:nterm]], 
                       score_contrib_1=v1[top_contrib_1[1:nterm]],
                       score_contrib_abst=rep(0,nterm) , stringsAsFactors=F) 
    
    df.abst <- data.frame(term=dictionary_abst[top_contrib_abst[1:nterm]], 
                          score_contrib_1=rep(0,nterm),
                          score_contrib_abst=v2[top_contrib_abst[1:nterm]],stringsAsFactors=F) 
    df <- rbind(df.1,df.abst)
    
    df <- cbind(aggregate(score_contrib_1 ~ term, data=df, FUN=sum),
                score_contrib_abst=aggregate(score_contrib_abst ~ term, data=df, FUN=sum)[,2])
    df$contrib <- alpha*df$score_contrib_1+(1-alpha)*df$score_contrib_abst
    
    outlist[[i]] <- df %>%
      filter(contrib>0) %>%
      mutate(rank=i)
  }
  rbind_all(outlist) %>%
    dplyr::select(term,contrib,rank) %>%
    group_by(term) %>%
    summarise(contrib_tot=sum(contrib)) %>%
    arrange(desc(contrib_tot))
}


#best <- best(nmatch = 15, nterm = 5, alpha=.5)

best <- best(nmatch = 15, nterm = length(unique(strsplit(query.limp$content[[1]]$content," ")[[1]])))

########################################################  wordcloud ##################################################

wordcloud(best$term,best$contrib_tot,
          scale=c(5,.7),
          min.freq=0.1,
          ordered.colors=T,
          colors=colorRampPalette(brewer.pal(9,"Set1"))(nrow(best)))




#########################################################################
#########################################################################
#########################################################################
#########################################################################










































#############################################  corups abstracts (abstracts) ##################################################

daux <- d %>%
  mutate(a=gsub('[-]|<br>',' ',Abstract),
         a=gsub('[()]|[.,;:`"*#&/><]|[\\\']|[]\\[]','',a),
         a=gsub(' +',' ',a),
         a=gsub('^ | $','',a)) %>%
  filter(a != ' ' , a != '', !grepl('(^([^ ] )+[^ ]$)|(^NA$)|(R o o t)', a))
aux <- daux$a

# creamos el corpus y limpiamos caracteres especiales
corpus.abstract <- Corpus(VectorSource(aux))


corp.2 <- tm_map(corpus.abstract,removeWords,stopwords("english"))
corp.2 <- tm_map(corp.2, function(x) stripWhitespace(tolower(x)))
corp.2 <- tm_map(corp.2,function(x){
  z <- strsplit(x, " +")[[1]]
  z.stem <- wordStem(z, language="english")
  PlainTextDocument(paste(z.stem, collapse=" "))
})

#################  Creacion de la matriz terminos documentos y los pesos por ntc (abstracts) ############################

#creamos la matriz terminos documentos
tdm.abst <- TermDocumentMatrix(corp.2, control=list(wordLengths=c(3, Inf)))
colnames(tdm.abst) <- seq(1,tdm.abst$ncol)

tdm.abst <- weightSMART(tdm.abst, spec = 'ntc')

##################################  revisamos la normalizacion de los pesos (abstracts) #########################################

head(sort(as.matrix(tdm.abst[,500]),dec=T))

################################################ Multiplicacion query * tdm (abstracts) ############################################

mat.abst <- sparseMatrix(i=tdm.abst$i, j=tdm.abst$j, x = tdm.abst$v)
dictionary_abst <- tdm.abst$dimnames$Terms
query.vec.abst <- TermDocumentMatrix(query.limp, 
                                  control = list(dictionary = dictionary_abst,
                                                 wordLengths=c(1, Inf))) 

query.vec.abst <- as.matrix(query.vec.abst)/sqrt(sum(query.vec.abst^2)) #normalizar con ntc el query

vec_abst <- t(mat.abst)%*%query.vec.abst

###################################################  top 15 docs (abstracts) ##################################################
idx_top_abst <- order(vec_abst, decreasing=T)

out_abst <- daux[idx_top_abst,] %>%
  dplyr::select(id,Title, Date, Sponsor, Abstract) %>%
  cbind(score_abst = sort(vec_abst,decreasing = T)) 

res_abstract <- out_abst %>% head(15)
res_abstract$Abstract <- gsub('<br>','',res_abstract$Abstract)
res_abstract$Title <- gsub('<br>','',res_abstract$Title)
res_abstract$Sponsor <- gsub('<br>','',res_abstract$Sponsor)

###################################################  left joins ##################################################

alpha <- .5

output <- d %>% 
  left_join(out_1[,c('id','score_1')], by = "id") %>%
  left_join(out_abst[,c('id','score_abst')], by = "id") %>%
  mutate(final_score=alpha*score_1+(1-alpha)*score_abst) %>%
  filter(final_score!=0) %>%
  arrange(desc(final_score)) 

res <- output %>% head(15)
res$Abstract <- gsub('<br>','',res$Abstract)
res$Title <- gsub('<br>','',res$Title)
res$Sponsor <- gsub('<br>','',res$Sponsor)
View(res)

##############################################  histograma de discriminacion ##########################################

m <- data.frame(min=min(res$final_score))
ggplot() +
  geom_bar(data=output, mapping=aes(x=final_score)) +
  geom_vline(data=res, aes(xintercept=min(final_score)), color='red')


##############################################  WordCloud ##########################################


best <- function(nmatch = 3, nterm = 5, alpha=.5){
    vq.1 <- query.vec.1
    vq.abst <- query.vec.abst
    
    outlist <- list()
    
    for(i in 1:nmatch){
    
        v.j.1 <- mat.1[,idx_top_1[i]]
        v.j.abst <- mat.abst[,idx_top_abst[i]]
        
        v1 <- v.j.1*vq.1
        v2 <- v.j.abst*vq.abst
        
        top_contrib_1 <- order(v1,decreasing=T)
        top_contrib_abst <- order(v2,decreasing=T)
        
        df.1 <- data.frame(term=dictionary_1[top_contrib_1[1:nterm]], 
                              score_contrib_1=v1[top_contrib_1[1:nterm]],
                              score_contrib_abst=rep(0,nterm) , stringsAsFactors=F) 
        
        df.abst <- data.frame(term=dictionary_abst[top_contrib_abst[1:nterm]], 
                              score_contrib_1=rep(0,nterm),
                              score_contrib_abst=v2[top_contrib_abst[1:nterm]],stringsAsFactors=F) 
        df <- rbind(df.1,df.abst)
        
        df <- cbind(aggregate(score_contrib_1 ~ term, data=df, FUN=sum),
                score_contrib_abst=aggregate(score_contrib_abst ~ term, data=df, FUN=sum)[,2])
        df$contrib <- alpha*df$score_contrib_1+(1-alpha)*df$score_contrib_abst
        
        outlist[[i]] <- df %>%
          filter(contrib>0) %>%
          mutate(rank=i)
    }
    rbind_all(outlist) %>%
      dplyr::select(term,contrib,rank) %>%
      group_by(term) %>%
      summarise(contrib_tot=sum(contrib)) %>%
      arrange(desc(contrib_tot))
}


#best <- best(nmatch = 15, nterm = 5, alpha=.5)

best <- best(nmatch = 15, nterm = length(unique(strsplit(query.limp$content[[1]]$content," ")[[1]])))

########################################################  wordcloud ##################################################

wordcloud(best$term,best$contrib_tot,
          scale=c(5,.7),
          min.freq=0.1,
          ordered.colors=T,
          colors=colorRampPalette(brewer.pal(9,"Set1"))(nrow(best)))

###################################################  Info a guardar ##################################################


#save(d_fin,tdm.1,tdm.abst,daux,file='App_Shiny_def/data/data.Rdata')


