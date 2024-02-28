import sys
import node
import tree_reader
import tree_utils

def process_tax(t):
    return

def get_mrca_wnms(n,t):
    if len(n) == 1:
        for i in t.leaves():
            if i.label == n[0]:
                return i
    else:
        return tree_utils.get_mrca_wnms(n,t)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"paf tax")
        sys.exit(0)

    paf = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    tax = tree_reader.read_tree_file_iter(sys.argv[2]).__next__()
    
    for i in paf.leaves():
        i.data["original_name"] = i.label
        i.label = i.label.split("_")[-1]
    for i in tax.leaves():
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
        if count == 21:
            break
    print(tax.get_newick_repr(False))
