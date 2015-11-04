library(shiny)

shinyUI(fluidPage(
  img(src='logoitam.png', align = "right"),
  titlePanel(withMathJax("$$\\text{Análisis de access.log}$$")),
  sidebarLayout(
    sidebarPanel(
      radioButtons("var", "Variable a analizar:",
                   c("Código de respuesta" = "Response_Code",
                     "Usuarios" = "Host",
                     "Paginas" = "URL",
                     "Historico" = "date",
                     "Día de la semana" = "day_of_week",
                     "Mes"="month",
                     "Hora"="hour")),
      br()
      ,
      
      sliderInput("N", 
                  "Numero de registros", 
                  value = 5,
                  min = 1, 
                  max = 100)
    ),
    
    mainPanel(
      tabsetPanel(type = "tabs", 
                  tabPanel("Gráficos", plotOutput("plot", width = '6in', height = '5in')), 
                  tabPanel("Estadísticas", tableOutput("table"), 
                           downloadButton('downloadData', 'Descarga Consulta'),
                           downloadButton('downloadData_all', 'Descarga Datos'))
      )
    )
  )
))
