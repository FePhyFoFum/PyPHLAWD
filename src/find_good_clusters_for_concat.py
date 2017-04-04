import sys
import os
import node
from conf import DI

"""
this assumes that you have already run 
post_process_cluster_info.py startdir
"""

mat_nms = []
clusterind = {}
keepers = set()#node
percent = 0.2
atleastlength = 20


def record_info_table(infilecsv):
    tf = open(infilecsv,"r")
    mat = []
    #transpose the matrix
    first = True
    for i in tf:
        spls = i.strip().split(",")
        if len(spls) == 1:
            continue
        if first == True:
            first = False
            count = 0
            for j in spls[1:]:
                clusterind[count] = j
                mat.append(0)
                mat_nms.append([])
                count += 1
        else:
            count = 0
            for j in spls[1:]:
                if j == "x":
                    mat[count] += 1
                    mat_nms[count].append(spls[0])
                count += 1
    tf.close()

def check_info_table(tree):
    for i in tree.iternodes(order="POSTORDER"):
        if i.parent != None:
            for j in clusterind:
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                pinter = set(i.parent.data["names"]).intersection(set(mat_nms[j]))
                if len(inter) > 0 and len(pinter) == len(inter) and len(inter) == len(mat_nms[j]):
                    if len(inter) / float(len(i.data["names"])) > percent and len(inter) > atleastlength:
                        print i.label,clusterind[j],len(inter),len(i.data["names"])
                        keepers.add(clusterind[j].replace(".fa",".aln"))
        else:
            for j in clusterind:
                inter = set(i.data["names"]).intersection(set(mat_nms[j]))
                keep = False
                if len(i.data["names"]) > 100:
                    if len(inter)/float(len(i.data["names"])) > percent:
                        print clusterind[j],len(inter),len(i.data["names"])
                        keep = True
                else:
                    if len(inter)/float(len(i.data["names"])) > percent+0.5:
                        print clusterind[j],len(inter),len(i.data["names"])
                        keep = True
                if keep == True:
                    keepers.add(clusterind[j].replace(".fa",".aln"))
    return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "python "+sys.argv[0]+" startdir"
        sys.exit(0)

    cld = sys.argv[1]
    #take off the trailing slash if there is one
    if cld[-1] == "/":
        cld = cld[0:-1]

    count = 0
    tree = node.Node()
    nodes = {}
    firstnode = True
    
    #build a tree from the directory
    for root, dirs, files in os.walk(cld, topdown = True):
        if "clusters" in root:
            continue
        if "clusters" in dirs:
            if firstnode == True:
                tree.label = root.split("/")[-1]
                firstnode = False
                nodes[root.split("/")[-1]] = tree
            nd = nodes[root.split("/")[-1]]
            nd.data["dir"] = root
            nd.data["names"] = set()
            tf = open(root+"/"+root.split("/")[-1]+".table","r")
            for i in tf:
                spls = i.strip().split("\t")
                nd.data["names"].add(spls[4])
            tf.close()
            for j in dirs:
                if "clusters" not in j:
                    cnd = node.Node()
                    cnd.label = j
                    cnd.parent = nd
                    nd.add_child(cnd)
                    nodes[j] = cnd
            count += 1

    record_info_table(cld+"/info.csv")

    check_info_table(tree)
    print len(keepers)

    # do you want to rename these ones?
    rename = raw_input("Do you want to rename these clusters? y/n ")
    if rename == 'y':
        tab = cld+"/"+cld.split("/")[-1]+".table"
        rtn = cld.split("/")[-1]
        cmd = "python "+DI+"change_id_to_name_fasta_mult.py "+tab+" "+ " ".join([cld+"/clusters/"+i for i in keepers])
        #print cmd
        os.system(cmd)
        concat = raw_input("Do you want to concat? y/n ")
        if concat == 'y':
            cmd = "pxcat -s "+" ".join([cld+"/clusters/"+i+".rn" for i in keepers])+" -o "+cld+"/"+rtn+"_outaln -p "+cld+"/"+rtn+"_outpart"
            #print cmd
            os.system(cmd)

    #print "pxcat -s "+" ".join(keepers)+" -o outaln -p outpart "


