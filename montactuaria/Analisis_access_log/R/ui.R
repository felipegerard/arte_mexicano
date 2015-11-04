library(shiny)




# Define UI for random distribution application 
shinyUI(fluidPage(
  
  # Application title
  titlePanel(withMathJax("$$\\text{Análisis de access.log}$$")),
  
  # Sidebar with controls to select the random distribution type
  # and number of observations to generate. Note the use of the
  # br() element to introduce extra vertical spacing
  sidebarLayout(
    sidebarPanel(
      radioButtons("var", "Variable a analizar:",
                   c("Errores" = "Response_Code",
                     "Usuarios" = "Host",
                     "Paginas" = "URL",
                     "Historico" = "date")),
      br(),
      
      sliderInput("n", 
                  "Number of observations:", 
                  value = 500,
                  min = 1, 
                  max = 1000)
    ),
    
    # Show a tabset that includes a plot, summary, and table view
    # of the generated distribution
    mainPanel(
      tabsetPanel(type = "tabs", 
                  tabPanel("Plot", plotOutput("plot")), 
                  tabPanel("Summary", verbatimTextOutput("summary")), 
                  tabPanel("Table", tableOutput("table"))
      )
    )
  )
))


#       sliderInput('N', 'Número de Bootstraps (B)',
#                   value = 1000, min = 500, max = 10000, step = 100),
#       sliderInput('alpha', 'Nivel de confianza',
#                   value = 0.95, min = 0.05, max = .99, step = 0.1)
#       
#     ),
#     mainPanel(
#       tabsetPanel(
#         tabPanel('Histogram', plotOutput('hist', width = '8in', height = '6in')),
#         column(3,
#                verbatimTextOutput("L"),
#                verbatimTextOutput("z0"),
#                verbatimTextOutput("a")
#         )
#       )
#     )
#   )
# })