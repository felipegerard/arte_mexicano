library(shiny)
library(dplyr)
library(wordcloud)
library(tm)

# load('../../data/corpora/corpus_books_completo_stem.Rdata')
load('data/basics.Rdata')
load('../../data/tdms/tdm_books_logtfidf_stem.Rdata')


shinyServer(function(input, output){
  
  query <- reactive({
    ifelse(is.null(input$lang),
           input$query,
           removeWords(input$query, stopwords(input$lang)))
  })
      
  info <- reactive(
    analyze(query(),
            query_lang = input$lang,
            matriz = mat,
            dict = dictionary,
            meta = meta,
            min_wordlength = 2)
  )
  output$tabla <- renderDataTable(
    info()$info %>%
      rename(Libro=id,
             Idioma=lang,
             TF_IDF=score)
  )
  id <-reactive(info()$info$id[input$idx] %>% as.character)
  relevant <- reactive({
    relevant <- mat[,id()] * info()$query_vec
    notzero <- (relevant > 0)
    relevant <- data.frame(Palabra= rownames(relevant)[notzero],
                           Contribución = as.numeric(relevant[,1])[notzero])
    relevant
  })
  output$relevant <- renderDataTable(relevant())
  output$content <- renderUI({
    path <- '../../data/full-txt'
    txt <- VCorpus(URISource(paste(path, id(), sep = '/')))[[1]]$content
    query_grep <- info()$query_clean[[1]]$content %>%
      gsub(pattern = '^ ', replacement = '') %>%
      gsub(pattern = ' ', replacement = '|')
    matches <- grep(query_grep, txt, value = F, ignore.case = T)
    matches <- paste(matches, txt[matches], sep = ': ')
    HTML(paste(
      paste0('<b>Palabras: ', gsub('\\|',', ',query_grep), '</b>'),
      paste(matches, collapse = '<br/>'),
      sep = '<br/>'))
  })
  output$book <- renderText(id())
  output$query <- renderText(input$query)
  output$wordcloud <- renderPlot({
    set.seed(1234)
    wordcloud(relevant()$Palabra, relevant()$Contribución, max.words = 50)
  })
  
})
