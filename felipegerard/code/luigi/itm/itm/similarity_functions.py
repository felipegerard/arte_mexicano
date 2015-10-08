from collections import defaultdict

# Regresar similitudes de un objeto index en un diccionario
def index2dict(index, file_list, num_sims=5):
	file_list = [i.replace('.txt','') for i in file_list]
	sims = {} #defaultdict(dict)
	for i, idx in enumerate(index):
		s = []
		for j in range(len(file_list)):
			s.append({
				'name':file_list[j],
				'similarity':float(idx[j])
				}) # idx[j] es un numpy.float32 y no es compatible con JSON. Por eso lo hacemos float normal
		s = sorted(s, key = lambda item: item['similarity'], reverse=True)[:num_sims]
		sims[file_list[i]] = {
			i:s[i]
			for i in range(len(s))
		}
	return sims
