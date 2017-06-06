import sys
import os
import tree_reader
import conf
if conf.usecython:
    import cnode as node
else:
    import node

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" basedir .table rooted_tree"
        sys.exit(0)

    tab = open(sys.argv[2],"r")
    idn = {}
    for i in tab:
        spls = i.strip().split("\t")
        idn[spls[3]] = spls[4]
    tab.close()



    #tree will be the taxonomy tree
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
                nd.data["names"].add(spls[4].replace(" ","_"))
            tf.close()
            for j in dirs:
                if "clusters" not in j:
                    cnd = node.Node()
                    cnd.label = j
                    cnd.parent = nd
                    nd.add_child(cnd)
                    nodes[j] = cnd
            count += 1


    intree = tree_reader.read_tree_file_iter(sys.argv[3]).next()
    for i in intree.iternodes(order="POSTORDER"):
        lvsnms = set(i.lvsnms())
        for j in tree.iternodes(order="POSTORDER"):
            if lvsnms.issubset(j.data["names"]):
                j.set_dist_root()
                i.data["h"] = j.droot
                if len(i.children) > 0:
                    i.label = str(j.droot)
                break

    for i in intree.iternodes(order="POSTORDER"):
        if len(i.children) > 0:
            try:
                if max(i.children[0].data["h"],i.children[1].data["h"]) - min(i.children[0].data["h"],i.children[1].data["h"]) > 1:
                    print "error in ",i.get_newick_repr(False)
                    #sys.exit(0)
            except:
                continue
    print intree.get_newick_repr(False)+";"

        
