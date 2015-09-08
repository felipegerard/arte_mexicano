library(shiny)

shinyUI(function(input, output){
  fluidPage(
    titlePanel('log(TF)-IDF'),
    sidebarPanel(
      textInput('query', 'Entra texto aquí:', value = 'Diego Rivera y Frida Kahlo'),
      textInput('lang', 'Idioma:', value = ''),
      sliderInput('idx', '# recomendación a mostrar', 1, 10, 1, 1)
    ),
    mainPanel(
      tabsetPanel(
        tabPanel('Documentos', dataTableOutput('tabla')),
        tabPanel('Líneas relevantes',
                 h3(textOutput('book')),
#                  h6(textOutput('query')),
                 htmlOutput('content')
                 ),
        tabPanel('Palabras importantes',
                 plotOutput('wordcloud'),
                 dataTableOutput('relevant')
                 )
      )
    )
  )
})
