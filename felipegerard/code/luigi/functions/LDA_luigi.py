
class TrainLDA(luigi.Task):
  """Necesita corpus limpio por 
  idioma sin las stopwords
  viene del proceso de VECTORIZE"""
  date_interval = luigi.DateIntervalParameter()
  n_topics = luigi.IntParameter(default=30) #numero de topicos
  chunk_size = luigi.IntParameter(default=100)
  update_e = luigi.IntParameter(default = 0)
  n_passes = luigi.IntParameter(default=10) #numero de pasadas al corpus
  input_dir = luigi.Parameter()
  clean_dir = luigi.Parameter()
  model_dir = luigi.Parameter()


def requires(self):
  return Vectorize(self.input_dir, self.clean_dir, self.model_dir)


def runLDA(self):
  from gensim import corpora
  from gensim.models.ldamodel import LdaModel
  import pickle

  dicc = pickle.load( open( self.model_dir + '/' + 'diccionario.dict') )
  corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
  if dim(corpus) >= 1000:
    lda = LdaModel(corpus, id2word=dicc, num_topics=self.n_topics, update_every=self.update_e, chunksize=self.chunk_size, passes=self.n_passes)
  else:  
    lda = LdaModel(corpus, id2word=dicc, num_topics=self.n_topics)
  with self.output().open('w') as f:
      pickle.dump(lda, f)

def output(self):
    return luigi.LocalTarget(self.model_dir + '/' + 'lda-%s-%d.pickle' % (self.date_interval, self.n_topics))


