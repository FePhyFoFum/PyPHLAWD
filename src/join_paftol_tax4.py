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
    if rnd.parent == None:
        going = False
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
    if nd != rnd:
        print(nd.get_newick_repr(),rnd.label,file=sys.stderr)
    return rnd

class Bipart:
    def __init__ (self,lf,rt):
        self.left = lf
        self.right = rt
        self.union = lf.union(rt)

    def __str__(self):
        x = ",".join(list(self.left))
        y = ",".join(list(self.right))
        return x+" | "+y

    def conflict(self, inbp):
        if len(inbp.right.intersection(self.right)) > 0 and len(inbp.right.intersection(self.left)) > 0:
            if len(inbp.left.intersection(self.right)) > 0 and len(inbp.left.intersection(self.left)) > 0 :
                return True
        if len(inbp.left.intersection(self.left)) > 0 and len(inbp.left.intersection(self.right)) > 0:
            if len(inbp.right.intersection(self.left)) > 0 and len(inbp.right.intersection(self.right)) > 0:
                return True
        return False

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
    totaltaxorigset = set([i.data["original_name"] for i in tax.iternodes()])
    totaltaxsetnodes = {}
    for i in tax.iternodes():
        totaltaxsetnodes[i.label] = i
    paftaxset = set(paf.lvsnms())
    for i in tax.iternodes():
        i.data["bp"] = Bipart(set(i.lvsnms()),totaltaxset-set(i.lvsnms()))
    for i in paf.iternodes():
        i.data["bp"] = Bipart(set(i.lvsnms()),paftaxset-set(i.lvsnms()))
        i.data["skip"] = False

    for j in paf.iternodes():
        for i in tax.iternodes():
            if j.data["skip"]:
                continue
            if i.data["bp"].conflict(j.data["bp"]):
                print("NONMONO",i.label,file=sys.stderr)
                j.data["skip"] = True

    count= 0
    for i in paf.iternodes(order="postorder"):
        if i == paf:
            continue
        if i.data["skip"]:
            continue

        l = i.lvsnms()
        l = list(set(l).intersection(totaltaxset))
        if len(i.children) < 2 or len(l) < 2:
            continue
        p = get_mrca_wnms(l,tax) #might want to walk back
        lp = i.parent.lvsnms()
        lp = list(set(lp).intersection(totaltaxset))
        pp = get_mrca_wnms(lp,tax)
        if p == pp:
            #print(l)
            skip = False
            for j in i.children:
                if j.data["skip"] == True:
                    skip = True
                    break
            if skip == True:
                continue
            chds = set([])
            for j in i.children:
                s = set(j.lvsnms()).intersection(totaltaxset)
                if len(s) == 0:
                    continue
                for k in p.children:
                    ss = set(k.lvsnms()).intersection(s)
                    if len(ss) > 0:
                        chds.add(k)
                        break
            if len(chds) > 1:
                n = node.Node()
                for j in chds:
                    p.remove_child(j)
                    n.add_child(j)
                    j.parent = n
                p.add_child(n)
                n.parent = p
            #print(p.get_newick_repr())
        #k = walk_back_mrca(p,taxoriginal,paf.lvsnms())
        #if k.parent == None:
        #    continue
        count += 1
        #if count == 20:
        #    break
    for i in tax.iternodes():
        if len(i.children) == 0:
            if "original_name" in i.data:
                i.label = i.data["original_name"]
        else:
            i.label = ""
    print(tax.get_newick_repr(False)+";")
