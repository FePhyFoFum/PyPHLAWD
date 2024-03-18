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
# nd = the mrca in the tax
# ond = the mrca in the original tax tree incase there is non-monophyly
# paflvsnms = the paf tree lvs nms
def walk_back_mrca(nd,otax,paflvsnms):
    rnd = nd
    intn = intersect_taxa(rnd.lvsnms(),paflvsnms)
    going = True
    while going:
        nintn = intersect_taxa(rnd.parent.lvsnms(),paflvsnms)
        if nintn != intn:
            break
        else:
            # monophyly check
            lab = rnd.parent.label
            tnd = None
            for i in otax.iternodes():
                if lab == i.label:
                    tnd = i
                    break
            if tnd != None:
                ntint2 = intersect_taxa(tnd.lvsnms(),paflvsnms)
                if ntint2 != intn:
                    break
            # end monophyly check
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
    taxoriginal = tree_reader.read_tree_file_iter(sys.argv[2]).__next__()
    
    for i in paf.leaves():
        i.data["original_name"] = i.label
        i.label = i.label.split("_")[-1]
    taxnodestodo = {}# label, node
    for i in tax.iternodes():
        i.data["original_name"] = i.label
        i.label = "_".join(i.label.split("_")[0:-1])
        taxnodestodo[i.label] = i
    for i in taxoriginal.iternodes():
        i.data["original_name"] = i.label
        i.label = "_".join(i.label.split("_")[0:-1])

    totaltaxset = set([i.label for i in tax.iternodes()])
    going = True
    while going:
        for i in tax.iternodes():
            going = False
            if len(i.children) > 0:
                x = set(i.lvsnms()).intersection(set(paf.lvsnms()))
                if len(x) == 0:
                    continue
                j = get_mrca_wnms(list(x),paf)
                y = set(j.lvsnms()).intersection(totaltaxset)
                if len(y) > len(x):
                    going = True
                    print("NON MONO",i.label,file=sys.stderr)
                    pp = i.parent
                    for k in i.children:
                        pp.add_child(k)
                    pp.remove_child(i)
                    break

    count= 0
    for i in paf.iternodes(order="postorder"):
        l = i.lvsnms()
        l = list(set(l).intersection(totaltaxset))
        if len(i.children) < 2 or len(l) < 2:
            continue
        p = get_mrca_wnms(l,tax)
        chds = []
        for j in i.children:
            s = set(j.lvsnms()).intersection(totaltaxset)
            if len(s) == 0:
                continue
            k = get_mrca_wnms(list(s),tax)
            if k == None:
                continue
            k = walk_back_mrca(k,taxoriginal,paf.lvsnms())
            chds.append(k)
        if len(chds) == 1:
            continue
        n = node.Node()
        jep = False
        ppp = None
        potpr = []
        for j in chds:
            pp = j.parent # need to add here if it is non-monophyletic so that things get sunk as a result
            # basically need to get the old parent to the new parent and see if the old parent is in the clade of new parent, if not, remove the names
            if j == p:
                jep = True
                ppp = pp
            pp.remove_child(j)
            n.add_child(j)
            potpr.append(pp)
        if jep == False:
            p.add_child(n)
        else:
            ppp.add_child(n)
        for pp in potpr: #if they are off on their own remove
            if len(pp.children) == 0 and pp.parent != None:
                tp = pp.parent
                while tp != None:
                    tp.remove_child(pp)
                    if len(tp.children) == 0:
                        tp = tp.parent
                    else:
                        break
        count += 1
        #if count == 100:
        #    break
    #check monophyly
    for i in taxoriginal.iternodes():
        if len(i.children) == 0:
            continue
        for j in tax.iternodes():
            if len(j.children) == 0:
                continue
            if i.label == j.label:
                s1 = set(i.lvsnms())
                s2 = set(j.lvsnms())
                if s1 != s2:
                    print("WOULD DELETE",j.label,file=sys.stderr)
                j.label = ""
                j.data["original_name"] = ""
    for i in tax.iternodes():
        if "original_name" in i.data:
            i.label = i.data["original_name"]
    print(tax.get_newick_repr(False)+";")
