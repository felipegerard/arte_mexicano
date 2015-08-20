
library(tm)

dat <- read.table(file = 'code/text-mining/txt/full-psv/bow_complete.psv', header = F, sep = '|', quote = "", col.names = c('book','term','count'), colClasses = c('character','character','character'))
dim(dat)
head(dat)
