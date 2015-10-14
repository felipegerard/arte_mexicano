
from markdown import markdown

if __name__ == '__main__':
	o = markdown('Hola nigagagaag')
	with open('output.html', 'w') as f:
		f.write(o)