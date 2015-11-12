# -*- coding: utf-8 -*-

import luigi
from luigi import configuration
from luigi.s3 import S3Target, S3PathTask
from luigi import six
import unicodedata
import shutil
from pprint import pprint
import pandas as pd
import csv
import pickle
import inspect, os
import requests
from os import listdir
import numpy as np
import subprocess
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pandas.tools.plotting import bootstrap_plot
from pandas.tools.plotting import scatter_matrix


execfile('functions/functions.py')

#########################cuerpo luigi

class Inputlog(luigi.ExternalTask):
    filename = luigi.Parameter()

    def output(self):

        return luigi.LocalTarget(self.filename)

class Parsear(luigi.Task):
	input_file = luigi.Parameter()
	output_file = luigi.Parameter()
	#par = luigi.FloatParameter(default=10.0)

	def requires(self):
		return Inputlog(self.input_file)

	def output(self):
		return luigi.LocalTarget(self.output_file)
		#return luigi.LocalTarget(self.output_file + ".pd")
		#return luigi.LocalTarget("data/%s.pd" % self.output_file)

	def run(self):	

		with open(self.input().path) as f:
		    f = f.readlines()

		array=[]
		for i in range(len(f)):
			array.append(apache2_logrow(f[i]))


		df = pd.DataFrame(array)
		df.columns = ['Host','Log_Name1','Log_Name','Date_Time','Method','Response_Code','Bytes_Sent','URL','User_Agent']
	
		pd.to_pickle(df,self.output().path)  

class Usuario(luigi.Task):
	
	input_file = luigi.Parameter() 
	output_file = luigi.Parameter() 
	output_df = luigi.Parameter() 
	#input_df = luigi.Parameter() 
	#output_df1 = luigi.Parameter() 

	def requires(self):
		#return Parsear(self.input_file, self.output_df, self.par)
		return Parsear(self.input_file, self.output_file)

	def output(self):      
		
		return luigi.LocalTarget(self.output_df)
		

	def run(self):
		df=pd.read_pickle(self.input().path)
		#df=pd.read_pickle(self.output().path)
		df=df.drop_duplicates(['Host', 'Date_Time','URL'])
		df = df.sort(['Host', 'Date_Time','Response_Code'], ascending=[1,1,0])
		df["Date_Time"] = df["Date_Time"].map(lambda x: str(x)[0:20])
		df = df.drop(df.index[[len(df)-1]])

		print df.head()

		pd.save(df,self.output().path)  


class Sesionizar(luigi.Task):
	
	input_file = luigi.Parameter() 
	output_file = luigi.Parameter() 
	output_df = luigi.Parameter() 
	#input_df = luigi.Parameter() 
	output_df1 = luigi.Parameter() 

	def requires(self):
		#return Parsear(self.input_file, self.output_df, self.par)
		return Usuario(self.input_file, self.output_file,self.output_df)

	def output(self):      
		
		return luigi.LocalTarget(self.output_df1)
		

	def run(self):
		df=pd.read_pickle(self.input().path)
		#
		df['Date_Time'] =  pd.to_datetime(df['Date_Time'], format='%d/%b/%Y:%H:%M:%S')
		df['id'] = df['Date_Time'].map(str)+df['Response_Code']+df['URL']
		df['Rank'] = df.groupby(['Host'])['id'].rank(ascending=True)
		#df['Date_Time'] = pd.to_datetime(df['Date_Time'])
		df = df.sort(['Host', 'Date_Time','Rank'], ascending=[1,1,0])
		df['time_diff'] = df.groupby('Host')['Date_Time'].diff()
		df['time_diff'] = df['time_diff'].fillna(0)

		print df.head()

		pd.save(df,self.output().path)  

class Enriquecer(luigi.Task):
	
	input_file = luigi.Parameter() 
	output_file = luigi.Parameter() 
	output_df = luigi.Parameter() 
	#input_df = luigi.Parameter() 
	output_df1 = luigi.Parameter() 
	output_df2 = luigi.Parameter()

	def requires(self):
		#return Parsear(self.input_file, self.output_df, self.par)
		return Sesionizar(self.input_file, self.output_file, self.output_df, self.output_df1)

	def output(self):      
		
		return luigi.LocalTarget(self.output_df2)
		#return luigi.LocalTarget('%s.csv' % self.output_df2)
		#df.to_csv("/Users/carlosmunguia/Desktop/conacyt/file_name.csv")

	def run(self):
		df=pd.read_pickle(self.input().path)
		#
		df['year'] = pd.DatetimeIndex(df['Date_Time']).year
		df['month'] = pd.DatetimeIndex(df['Date_Time']).month
		df['day'] = pd.DatetimeIndex(df['Date_Time']).day
		df['hour'] = pd.DatetimeIndex(df['Date_Time']).hour
		df["date"] =  pd.DatetimeIndex(df['Date_Time']).date
		df['day_of_week'] = df['Date_Time'].dt.dayofweek
		days = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado',6:'Domingo'}
		df['day_of_week'] = df['day_of_week'].apply(lambda x: days[x])
		df['dif_seg_clicks'] = df['time_diff'].apply(lambda x: x  / np.timedelta64(1,'s')).astype('int64') % (24*60)
		df.loc[df.dif_seg_clicks == 0, ['dif_seg_clicks']] = 1
		print self.input().path

		pd.save(df,self.output().path)  

		df.to_csv('%s.csv' % self.input().path)
        


class Reportes(luigi.Task):
	
	input_file = luigi.Parameter() 
	output_file = luigi.Parameter() 
	output_df = luigi.Parameter() 
	#input_df = luigi.Parameter() 
	output_df1 = luigi.Parameter() 
	output_df2 = luigi.Parameter()
	#output_df3 = luigi.Parameter()
	par = luigi.FloatParameter(default=10.0)
	ydate = luigi.Parameter()
	wdate = luigi.Parameter()
	

	def requires(self):
		#return Parsear(self.input_file, self.output_df, self.par)
		#return luigi.LocalTarget("data/%s.pd" % self.output_file)
		return Enriquecer(self.input_file, self.output_file, self.output_df, self.output_df1, self.output_df2)

	def output(self):      
		
		return {
					'images':luigi.LocalTarget("Metrics_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf"),
					'errors':luigi.LocalTarget("error_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf"),
					'users':luigi.LocalTarget("users_" + str(self.wdate) + "_to_" + str(self.ydate)+ ".pdf")#,
				}

		#return luigi.LocalTarget(self.output_df3)

	def run(self):
		df=pd.read_pickle(self.input().path)
		#df = pd.read_csv(self.input().path)
		#
		def subconjunto(x,par):
		    x=df[x.dif_seg_clicks < par*60+1]
		    return x

		df1=subconjunto(df,self.par)

		#df1.loc[df1.dif_seg_clicks == 0, ['dif_seg_clicks']] = 1

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

		#pd.save(df1,self.output().path) 
		#pd.df1.to_csv

if __name__ == '__main__':
	luigi.run()
