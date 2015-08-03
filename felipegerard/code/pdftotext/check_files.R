
library(dplyr)
setwd('~/data-science/arte-mexicano/felipegerard/code/pdftotext/txt')

loc <- read.csv('data_frame_local.psv', header = F, sep = '|', colClasses=c('numeric','character'))
names(loc) <- c('n','book')

all <- read.csv('data_frame_allfiles.psv', header = F, sep = '|', colClasses=c('numeric','character'))
names(all) <- c('n','book')

head(loc)
head(all)

res <- full_join(all, loc, by='book') %>%
  mutate(dif = abs(n.x - n.y))

res %>% filter(dif >= 2)
res %>% filter(is.na(dif)) %>% View

table(res$dif)
