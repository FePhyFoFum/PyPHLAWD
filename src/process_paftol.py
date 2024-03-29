import sys

import node
import tree_reader
import tree_utils

def get_name(nm):
    nm = nm.replace("'","").replace(" ","_")
    nm = "_".join(nm.split("_")[:-1])
    return nm


"""
dealing with non-monophyly
"""
def remove_non_mono(t):
    ky = []
    rm = []
    for i in t.leaves():
        if i.label not in ky:
            ky.append(i.label)
        else:
            rm.append(i)
    for i in rm:
        p = i.parent
        p.remove_child(i)
        pp = p.parent
        for j in p.children:
            pp.add_child(j)
        pp.remove_child(p)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python",sys.argv[0],"tre")
        sys.exit(0)

    t = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    for i in t.leaves():
        i.label = get_name(i.label)

    # check for monophyly and sink
    going = True
    while going:
        going = False
        for i in t.iternodes("postorder"):
            lvs = i.leaves()
            x = set(i.lvsnms())
            if len(x) == 1 and len(lvs) > 1:
                going = True
                p = i.parent
                i.parent.children.remove(i)
                i.parent = None
                nd = node.Node()
                nd.istip = True
                nd.label = list(x)[0]
                p.add_child(nd)
                break
    going = True
    while going:
        going = False
        for i in t.iternodes():
            if len(i.children) == 1:
                p = i.parent
                c = i.children[0]
                p.children.remove(i)
                i.parent = None
                p.add_child(c)
                going = True
    remove_non_mono(t)
    print(t.get_newick_repr(False)+";")
