
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import inspect
import re


class InputText(luigi.ExternalTask):
    """
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    filename = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present in the local file system.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """

        # The directory containing this file
        root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"
        return luigi.LocalTarget(root + self.filename)

class CleanText(luigi.Task):
	"""docstring for CleanText"""
	input_dir = luigi.Parameter()
	output_dir = luigi.Parameter()

	def requires(self):
		return [ InputText(self.input_dir + '/' + filename)
				for filename in os.listdir(self.input_dir) ]	
	
	def run(self):
		for inp, outp in zip(self.input(), self.output()):
			fi = inp.open('r')
			fo = outp.open('w')
			txt = fi.read()#.decode('utf-8').lower()
			txt = self.clean_text(txt)
			fo.write(txt)
			fi.close()
			fo.close()

	def output(self):
		# return luigi.LocalTarget(self.output_dir + '/' + 'prueba.txt')
		return [ luigi.LocalTarget(self.output_dir + '/' + filename)
				for filename in os.listdir(self.input_dir) ]

	def clean_text(self, d):
	    '''d debe ser un string en unicode'''
	    d = re.sub('[^a-z0-9áéíóúñäëïöü]', ' ', d)
	    d = re.sub(' +', ' ', d)
	    d = re.sub(' ([^ ]{1,3} )+', ' ', d, )
	    d = re.sub(' [^ ]*(.)\\1{2,}[^ ]* ', ' ', d)
	    return d


class GenerateDictionary(luigi.Task):
	"""Docstring"""
	


if __name__ == '__main__':
	luigi.run()











