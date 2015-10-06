
# Regresar similitudes de un objeto index
def arrange_similarities(index, file_list, num_sims=5):
    sims = []
    for i, idx in enumerate(index):
        s = []
        for j in range(len(file_list)):
            s.append((i,j,file_list[i],file_list[j],idx[j]))
        s = sorted(s, key = lambda item: item[4], reverse=True)
        sims += s
    return sims