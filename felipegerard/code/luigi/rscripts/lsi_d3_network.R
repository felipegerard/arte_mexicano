#! /usr/bin/env Rscript

library(dplyr)
library(networkD3)
library(optparse)

### PARAMS
option_list = list(
  make_option(c('--input','-f'), type = 'character', default = NULL),
  make_option(c('--output','-t'), type = 'character', default = NULL),
  make_option(c('--max_links'), type = 'integer', default = 5),
  make_option(c('--min_sim'), type = 'numeric', default = 0)
)
opt <- parse_args(OptionParser(option_list = option_list))

print(opt)

max_links <- opt$max_links #3 #$(max_links)s
min_sim <- opt$min_sim #0.3 #$(min_sim)s
orig <- read.csv(opt$input) %>%
  group_by(from) %>%
  top_n(max_links) %>%
  filter(sim >= min_sim)

nodes <- rbind(data.frame(id = orig$from,
                          name = orig$from_name),
      data.frame(id = orig$to,
                 name = orig$to_name)) %>%
  unique %>%
  arrange(id) %>%
  mutate(group = 1)

links <- orig[c('from', 'to', 'sim')]

print('Creando...')
net <- forceNetwork(links,
                    nodes,
                    Source = 'from', Target = 'to',
                    NodeID = 'name', Group = 'group',
                    Value = 'sim',
                    zoom = TRUE)

print('Guardando...')
saveNetwork(net, file = opt$output, selfcontained = T)
print('LISTO')





