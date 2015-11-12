library(shiny)
library(ggplot2)
library(dplyr)
library(parallel)

logs <- as.data.frame(read.csv("~/Desktop/conacyt/enriquecer.csv"))

options(digits=4)

mytable <- function(x, var, mc.cores=4) x %>% group_by_(var) %>%
  summarise(n = n(),dif_seg_clicks=mean(dif_seg_clicks),KBytes_Sent=mean(Bytes_Sent)/1024) %>% 
  mutate(porc=n/sum(n)*100)%>%arrange(desc(porc))


shinyServer(function(input, output, session) {

  data <- reactive({
    var <- switch(input$var,
                  Response_Code="Response_Code",
                  Host="Host",
                  URL="URL",
                  date="date",
                  day_of_week="day_of_week",
                  month="month",
                  hour="hour",
                  "Response_Code")
    
    mytable(logs, var, mc.cores=4)
  })
  
  output$plot <- renderPlot({
    
    df<-as.data.frame(data())%>%head(input$N)
    colnames(df)<-c("Variable","N","Promedio_segundos","Promedio_KB","Porcentaje")
    
    ggplot(df,aes(x=reorder(Variable,Porcentaje),y = Porcentaje))+
      geom_bar(stat="identity",fill=sample(colours(), 1), colour=sample(colours(), 1))+
      labs(x =colnames(data())[1], y = "Porcentaje")+
      theme_minimal()+
      theme(plot.title = element_text(size = rel(.8)), 
            legend.title = element_text(size=3),
            axis.text.x = element_text(angle = 45, hjust = 1, size = 8))
    
    
  })
  
  output$table <- renderTable({
    
    df<-as.data.frame(data()%>%head(input$N))
    colnames(df)<-c("Variable","N","Promedio_segundos","Promedio_KB","Porcentaje")
    data.frame(df)
  })
  
  output$downloadData <- downloadHandler(
    filename = function() { 
      paste(colnames(data())[1],"_",Sys.Date(), '.csv', sep='') 
    },
    content = function(file) {
      write.csv(as.data.frame(data()%>%head(input$N)), file)
    }
  )
  
  
  output$downloadData_all <- downloadHandler(
    filename = function() { 
      paste("Datos_logs","_",Sys.Date(), '.csv', sep='') 
    },
    content = function(file) {
      write.csv(logs, file)
    }
  )
  
})


####################







