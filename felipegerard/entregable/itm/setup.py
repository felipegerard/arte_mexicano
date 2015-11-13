from setuptools import setup

setup(name='itm',
	version='0.2',
	description='Extraccion y mineria de textos.',
	url='http://github.com/felipegerard/arte_mexicano_antiguo',
	author='Felipe Gerard',
	author_email='felipegerard@gmail.com',
	license='Apache 2.0',
	packages=['itm'],
	scripts=['bin/itam-tm', 'bin/itam-tm-default', 'bin/itam-d3-network.R'],
	install_requires=[
		'luigi>=1.3.0',
		'numpy>=1.8.2',
		'scipy>=0.7.0',
		'pdfminer>=20140328',
		'gensim>=0.12.1',
		'pandas>=0.17.0',
		'nltk>=3.0.5',
		'markdown>=2.6.2',
		'PyPDF2>=1.25.1'
		],
	zip_safe=False)
