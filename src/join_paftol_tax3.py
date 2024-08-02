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
        p = get_mrca_wnms(l,tax)
        chds = set([])
        for j in i.children:
            s = set(j.lvsnms()).intersection(totaltaxset)
            if len(s) == 0:
                continue
            for k in p.children:
                ss = set(j.lvsnms()).intersection(s)
                if len(ss) > 0:
                    chds.add(k)
        if len(chds) == 1:
            continue
        break
        n = node.Node()
        jep = False
        ppp = None
        potpr = []
        for j in list(chds):
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
