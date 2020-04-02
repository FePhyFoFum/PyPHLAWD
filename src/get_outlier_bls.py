import tree_reader
import sys
import numpy as np
import scipy.stats

def mn_conf_interval(data, confidence=0.99):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

def outliers(tree,lower,upper):
    ret = []
    for i in tree.iternodes():
        if i.length > upper:
            ret.append(i)
    return ret

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("python "+sys.argv[0]+" infile.tre")
        sys.exit(0)
    f = open(sys.argv[1],"r")
    ts = f.readline()
    tree = tree_reader.read_tree_string(ts)
    f.close()
    allbls = []
    for i in tree.iternodes():
        allbls.append(i.length)

    mn,low,high = mn_conf_interval(allbls)
    #print(mn,low,high)
    for i in outliers(tree,low,high):
        print(i.length,i.get_newick_repr(False))
    
