import sys
import sqlite3
import tree_reader
import node
import tree_utils
from get_ncbi_ids_for_names import get_taxid_for_name_limit_left_right

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python",sys.argv[0],"paftol otherconstraint db")
        sys.exit(0)
    paft = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    cons = tree_reader.read_tree_file_iter(sys.argv[2]).__next__()
    dbname = sys.argv[3]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    left = 0
    right = 0
    c.execute("select left_value,right_value from taxonomy where name = 'Viridiplantae';")
    for i in c:
        left = str(i[0])
        right = str(i[1])
    for i in cons.leaves():
        c.execute("select name from taxonomy where name_class = 'scientific name' and ncbi_id = ?;",(i.label,))
        genus = None
        for j in c:
            genus = j[0].split(" ")[0]
            break
        gid = get_taxid_for_name_limit_left_right(c,genus,left,right)
        i.data["orig"] = i.label
        i.label = gid
    for i in paft.leaves():
        spls = i.label.split("_")
        i.data["orig"] = i.label
        i.label = spls[-1]
    conslvs = cons.lvsnms()
    conslvs = list(set(cons.lvsnms()).intersection(set(paft.lvsnms())))
    #print(conslvs)
    paftmrca = tree_utils.get_mrca_wnms(conslvs,paft)
    #print(paftmrca.get_newick_repr())
    for i in paftmrca.iternodes(order="postorder"):
        if len(i.children) > 2 or len(i.children) == 0:
            continue
        lf = i.children[0]
        rt = i.children[1]
        #print("l",lf.get_newick_repr(),file=sys.stderr)
        #print("r",rt.get_newick_repr(),file=sys.stderr)
        if len(set(lf.lvsnms()).intersection(conslvs))==0:
            continue
        if len(set(rt.lvsnms()).intersection(conslvs))==0:
            continue
        if len(lf.lvsnms()) == 1:
            if cons.lvsnms().count(lf.lvsnms()[0]) == 1:
                for j in cons.leaves():
                    if j.label == lf.lvsnms()[0]:
                        lfmrca = j
            else:
                lfmrca = tree_utils.get_mrca_wnms(lf.lvsnms(),cons)
        else:
            lfmrca = tree_utils.get_mrca_wnms(lf.lvsnms(),cons) 
        if len(rt.lvsnms()) == 1:
            if cons.lvsnms().count(rt.lvsnms()[0]) == 1:
                for j in cons.leaves():
                    if j.label == rt.lvsnms()[0]:
                        rtmrca = j
            else:
                rtmrca = tree_utils.get_mrca_wnms(rt.lvsnms(),cons)
        else:
            rtmrca = tree_utils.get_mrca_wnms(rt.lvsnms(),cons) 
        if rtmrca == lfmrca:
            continue
        if rtmrca.parent == lfmrca.parent:
            nd = node.Node()
            ndp = rtmrca.parent
            nd.parent = ndp
            ndp.remove_child(rtmrca)
            ndp.remove_child(lfmrca)
            nd.add_child(rtmrca)
            nd.add_child(lfmrca)
            ndp.add_child(nd)
            #print(nd.get_newick_repr())
            #print(nd.parent.get_newick_repr())
    for i in cons.leaves():
        i.label = i.data["orig"]
    print(cons.get_newick_repr()+";")