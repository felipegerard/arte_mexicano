# coding=utf-8

import os

with open('vitral.txt') as f:
	s = f.read()


def get_extracts(string, min_length=500, percentages=[0.1,0.5,0.9]):
	str_list = string.split('\n')
	positions = [int(p*len(str_list)) for p in percentages]
	extracts = []

	for p in positions:
		s = ''
		for i in range(p, p + 10, 1):
			if len(str_list[i]) > 0 and str_list[i][0].isupper():
				break
			p = p + 1
		for i in range(p, p + 20, 1):
			if len(s) >= min_length:
				break
			else:
				s += str_list[i]
		extracts.append({'start_line':p, 'start_line_perc':round(1.0*p/len(str_list),3), 'text':s})
	return extracts

get_extracts(s)

x = {}
for f in os.listdir('.'):
	with open(f) as c:
		s = c.read()
	x[f] = get_extracts(s)


min_length = 500
percentages = [0.1, 0.5, 0.9]
positions = [int(p*len(l)) for p in percentages]
extracts = []

for p in positions:
	s = ''
	for i in range(p, p + 10, 1):
		if len(l[i]) > 0 and l[i][0].isupper():
			break
		p = p + 1
	for i in range(p, p + 20, 1):
		if len(s) >= min_length:
			break
		else:
			s += l[i]
	extracts.append(s)





