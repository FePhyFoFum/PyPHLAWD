import sys

import tree_reader
import tree_utils
import node

def get_mrca_int(nms1,nms2,tr,verb):
    nds1 = []
    for i in tr.iternodes():
        if i.label in nms1:
            nds1.append(i)
    nds2 = []
    for i in tr.iternodes():
        if i.label in nms2:
            nds2.append(i)
    ndsa = [i for i in nds1]
    ndsa.extend(nds2)
    if len(ndsa) == 0:
        for i in tr.iternodes():
            print(i.label,file=sys.stderr)
        print(nms1,nms2,file=sys.stderr)
        sys.exit(0)
    if len(ndsa) == 1:
        pa = ndsa[0]
    else:
        pa = tree_utils.get_mrca(ndsa,tr)
    x1 = None
    x2 = None
    for i in pa.children:
        si = set([nd for nd in i.iternodes()])
        if set(nds1).intersection(si) == set(nds1):
            x1 = i
        if set(nds2).intersection(si) == set(nds2):
            x2 = i
    return x1,x2,pa

def remove_knee(tr):
    going = True
    while going:
        going = False
        for i in tr.iternodes():
            if len(i.children) == 1:
                going = True
                p = i.parent
                #print(p.get_newick_repr(False),file=sys.stderr)
                c = i.children[0]
                p.remove_child(i)
                p.add_child(c)
                if i.label != "":
                    if c.label == "":
                        c.label = i.label
                    elif p.label == "":
                        p.label = i.label
                #print(p.get_newick_repr(False),file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"bigtree smalltree")
        sys.exit(0)
    bt = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    st = tree_reader.read_tree_file_iter(sys.argv[2]).__next__()

    for i in bt.iternodes():
        i.data["original_name"] = i.label
        i.label = i.label.split("_")[-1]

    #remove root st
    nt = st.children[0]
    if len(nt.leaves()) == 1:
        nt = st.children[1]

    for i in nt.iternodes("postorder"):
        verb = False
        if len(i.leaves()) < 2:
            continue
        lvs1 = i.children[0].lvsnms()
        lvs2 = i.children[1].lvsnms()
        #print(lvs1,file=sys.stderr)
        #print(lvs2,file=sys.stderr)
        m1,m2,pa = get_mrca_int(lvs1,lvs2,bt,verb)
        #print(m1.get_newick_repr(False),file=sys.stderr)
        #print(m2.get_newick_repr(False),file=sys.stderr)
        #print(pa.get_newick_repr(False),file=sys.stderr)
        if m1 == m2:
            continue
        if m1 == None or m2 == None:
            continue
        nd = node.Node()
        pa.remove_child(m1)
        pa.remove_child(m2)
        nd.add_child(m1)
        nd.add_child(m2)
        nd.length = i.length
        m1.length = i.children[0].length
        m2.length = i.children[1].length
        pa.add_child(nd)
    remove_knee(bt)
    for i in bt.iternodes():
        if "original_name" in i.data:
            i.label = i.data["original_name"]
    print(bt.get_newick_repr(True)+";")

