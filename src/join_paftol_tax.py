import sys
import node
import tree_reader
import tree_utils

"""
TODO
- need to do the mrca using names that includes internal nodes
- need to go back to the node that is the MRCA but includes the clade of unsampled 
so if it is 
(a,b,c),(d,e,f) and i have (((e,f),d),a) -> ((a,b,c),(d,(e,f)))

"""

def process_tax(t):
    return

def intersect_taxa(n,t):
    return len(set(n).intersection(t))

def get_mrca_wnms(n,t):
    if len(n) == 1:
        for i in t.iternodes():
            if i.label == n[0]:
                return i
    else:
        return tree_utils.get_mrca_wnms(n,t)

# n = names that we wanted to get mrca
# nd = the mrca
# paflvsnms = the paf tree lvs nms
def walk_back_mrca(nd,paflvsnms):
    rnd = nd
    intn = intersect_taxa(rnd.lvsnms(),paflvsnms)
    going = True
    while going:
        nintn = intersect_taxa(rnd.parent.lvsnms(),paflvsnms)
        if nintn != intn:
            break
        else:
            if rnd.parent == None:
                break
            rnd = rnd.parent
    return rnd

        


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"paf tax")
        sys.exit(0)

    paf = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    tax = tree_reader.read_tree_file_iter(sys.argv[2]).__next__()
    
    for i in paf.leaves():
        i.data["original_name"] = i.label
        i.label = i.label.split("_")[-1]
    for i in tax.iternodes():
        i.data["original_name"] = i.label
        i.label = i.label.split("_")[0]
    count= 0
    for i in paf.iternodes(order="postorder"):
        if len(i.children) < 2:
            continue
        l = i.lvsnms()
        print(l,file=sys.stderr)
        p = get_mrca_wnms(l,tax)
        chds = []
        for j in i.children:
            k = get_mrca_wnms(j.lvsnms(),tax)
            if k == None:
                continue
            k = walk_back_mrca(k,paf.lvsnms())
            chds.append(k)
        if len(chds) == 1:
            continue
        n = node.Node()
        for j in chds:
            pp = j.parent # need to add here if it is non-monophyletic so that things get sunk as a result
            pp.remove_child(j)
            n.add_child(j)
        p.add_child(n)
        count += 1
        #if count == 100:
        #    break
    print(tax.get_newick_repr(False))
