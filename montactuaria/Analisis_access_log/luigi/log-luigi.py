# -*- coding: utf-8 -*-

import luigi
from luigi import configuration
from luigi.s3 import S3Target, S3PathTask
import unicodedata
import shutil
from pprint import pprint
import pandas as pd
import csv
import pickle
import inspect, os
import requests
import datetime as dt
from os import listdir
import numpy as np
import subprocess
from luigi import six
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pandas.tools.plotting import bootstrap_plot
from pandas.tools.plotting import scatter_matrix


#########################cuerpo luigi

class Inputcsv(luigi.ExternalTask):
    filename = luigi.Parameter()

    def output(self):

        # The directory containing this file
        #root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"
        return luigi.LocalTarget(self.filename)

class Crea_df(luigi.Task):
	input_file = luigi.Parameter()
	output_file = luigi.Parameter()
	par = luigi.FloatParameter(default=10.0)

	def requires(self):
		return Inputcsv(self.input_file)

	def output(self):
		return luigi.LocalTarget(self.output_file)

	def run(self):
		df = pd.read_csv(self.input().path)

		############bajo el supuesto que el host(ip) sea el usuario unico, sino, sólo hay que adecuar el paste
		df['id'] = df['Date_Time'].map(str) + df['URL']
		df['Rank'] = df.groupby(['Host'])['id'].rank(ascending=True)

		df['Date_Time'] = pd.to_datetime(df['Date_Time'])
		df['time_diff'] = df.groupby('Host')['Date_Time'].diff()
		df['time_diff'] = df['time_diff'].fillna(0)

		df['year'] = pd.DatetimeIndex(df['Date_Time']).year
		df['month'] = pd.DatetimeIndex(df['Date_Time']).month
		df['day'] = pd.DatetimeIndex(df['Date_Time']).day
		df['hour'] = pd.DatetimeIndex(df['Date_Time']).hour

		df['day_of_week'] = df['Date_Time'].dt.dayofweek
		days = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado',6:'Domingo'}
		df['day_of_week'] = df['day_of_week'].apply(lambda x: days[x])


		df['dif_seg_clicks'] = df['time_diff'].apply(lambda x: x  / np.timedelta64(1,'s')).astype('int64') % (24*60)

		#################################mandarlo a funciones
		def subconjunto(x,par):
		    x=df[x.dif_seg_clicks < par*60+1]
		    return x

		df1=subconjunto(df,self.par)
		pd.save(df1,self.output().path)

class Reporte(luigi.Task):
	# Parametros de crea_df
	input_file = luigi.Parameter() #csv_output_file1.csv
	#output_file = luigi.Parameter() #pruebapandas2.pd
	

	# Parametros de reporte
	output_df = luigi.Parameter() #pruebapandas2.pd
	# fechas
	par = luigi.FloatParameter(default=10.0)
	ydate = luigi.Parameter()
	wdate = luigi.Parameter()
	#output_img = luigi.Parameter()
	#output_err = luigi.Parameter()
	#output_usr = luigi.Parameter()

	def requires(self):
		return Crea_df(self.input_file, self.output_df, self.par)

	def output(self):
		return {
					'images':luigi.LocalTarget("Metrics_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf"),
					'errors':luigi.LocalTarget("error_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf"),
					'users':luigi.LocalTarget("users_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf")#,
				}

	def run(self):
		#df = pd.read_csv(self.input().path)
		df1 = pd.load(self.input().path)
		df1.loc[df1.dif_seg_clicks == 0, ['dif_seg_clicks']] = 1
		print df1.head()

		##Análisis de páginas más visitadas)
		grouped = df1.groupby('URL')
		paginas=grouped['dif_seg_clicks'].agg([np.count_nonzero, np.mean]).sort('count_nonzero', ascending=[False])
		paginas.columns=['Numero_visitas', 'tiempo_promedio']


		##Analisis de Logs de Servidores WEB
		grouped = df1.groupby('Response_Code')
		error=grouped['dif_seg_clicks'].agg([np.size]).sort('size', ascending=[False])/len(df1)*100
		error.columns=['Porcentaje_errores']

		#Quién consulta más documentos
		grouped = df1.groupby('Host')
		usuarios=grouped['dif_seg_clicks'].agg([np.count_nonzero, np.mean]).sort('count_nonzero', ascending=[False])
		usuarios.columns=['Numero_visitas' ,'tiempo_promedio']

		##historico
		grouped = df1.groupby('day')
		tiempo=grouped['dif_seg_clicks'].agg([np.count_nonzero]).sort('count_nonzero', ascending=[False])
		tiempo.columns=['Numero_visitas']

		#######generación reportes

		#ydate = "2014-09-09"
		#wdate = "2014-08-31"

		pdf_name = self.output()['images'].path #"Metrics_" + str(wdate) + "_to_" + str(ydate)+ ".pdf"
		pdf = PdfPages(pdf_name)

		#P & C over time
		#ts2.plot(secondary_y=["P"])
		error.plot(kind='bar',alpha=0.5, stacked=True)
		pdf.savefig()

		#Density Plot of Conversion
		paginas.head(10).plot(kind='barh',alpha=0.5)
		pdf.savefig()

		#scatter matrix on the data_frame
		#scatter_matrix(ts, alpha=0.2, figsize=(6, 6), diagonal='kde')
		usuarios.head(10).plot(kind='bar',alpha=0.5)
		pdf.savefig()

		tiempo.plot(kind='area')
		pdf.savefig()
		pdf.close()		


		##########################terminan graficos

		template = r'''\documentclass[preview]{{standalone}}
		\usepackage{{booktabs}}
		\begin{{document}}
		{}
		\end{{document}}
		'''

		filename = self.output()['users'].path.replace('.pdf', '.tex') #'out.tex'
		pdffile = self.output()['users'].path#'out.pdf'
		outname = self.output()['users'].path.replace('.pdf', '.png')


		with open(filename, 'wb') as f:
		    f.write(template.format(usuarios.head(20).to_latex()))
		subprocess.call(['pdflatex', filename])
		subprocess.call(['convert', '-density', '300', pdffile, '-quality', '90', outname],shell=True)


		###############################el otro

		filename1 = self.output()['errors'].path.replace('.pdf', '.tex') #'out.tex'
		pdffile1 = self.output()['errors'].path#'out.pdf'
		outname1 = self.output()['errors'].path.replace('.pdf', '.png')


		with open(filename1, 'wb') as f:
		    f.write(template.format(error.to_latex()))
		subprocess.call(['pdflatex', filename1])
		subprocess.call(['convert', '-density', '300', pdffile1, '-quality', '90', outname1],shell=True)


if __name__ == '__main__':
	luigi.run()
        