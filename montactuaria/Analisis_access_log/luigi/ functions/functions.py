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
from luigi import six
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB