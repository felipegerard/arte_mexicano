# coding=utf-8
import os
import re

def clean_text(d):
	'''d debe ser un string'''
	d = remove_accents(d)
	d = re.sub('\n', ' ', d)
	d = d.lower()
	d = re.sub('[^a-z0-9 ]', ' ', d)
	d = re.sub(' +', ' ', d)
	d = re.sub(' ([^ ]{1,3} )+', ' ', d, )
	d = re.sub(' [^ ]*(.)\\1{2,}[^ ]* ', ' ', d)
	return d

def remove_stopwords(clean_text, lang):
	content = clean_text.split(' ')
	return ' '.join([w for w in content if w not in stopwords.words(lang)])