library(shiny)
library(ggplot2)
#library(plyr)
library(dplyr)

logs <- as.data.frame(read.csv("~/Desktop/conacyt/pandas2.csv"))

library(shiny)

mytable <- function(x, ...) x %>% group_by_(...) %>% summarise(n = n()) %>% mutate(porc=n/sum(n)*100)



# Define server logic for random distribution application
shinyServer(function(input, output) {
  
  
  selectedData <- reactive({
    data[, c(input$xcol, input$ycol)]
  })
  
  # Reactive expression to generate the requested distribution.
  # This is called whenever the inputs change. The output
  # functions defined below then all use the value computed from
  # this expression
  data <- reactive({
    var <- switch(input$var,
                  Response_Code="Response_Code",
                  Host="Host",
                  URL="URL",
                  date="date",
                  "Response_Code")
    
    
    mytable(logs, var)
  })
  
  # Generate a plot of the data. Also uses the inputs to build
  # the plot label. Note that the dependencies on both the inputs
  # and the data reactive expression are both tracked, and
  # all expressions are called in the sequence implied by the
  # dependency graph
  output$plot <- renderPlot({
    #dist <- input$dist
  #n <- input$n
     
    hist(data()$n)
  })
  
  # Generate a summary of the data
  output$summary <- renderPrint({
    summary(data())
  })
  
  # Generate an HTML table view of the data
  output$table <- renderTable({
    data.frame(x=data())
  })
  
})


####################

# 
#head(logs)
# 
# 
# Response_Code<-
#   logs%>%
#   group_by_("Response_Code")%>%
#   summarise(n = n()) 
#   
# 
# summary(data)
#   
# detach("package:plyr", unload=TRUE) 
# 
# library(dplyr)
# 
#   
# #   
# data<-mytable(logs, "Response_Code")
# 
# hist(data$n)
# 
# summary(data)
  