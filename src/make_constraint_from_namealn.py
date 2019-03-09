import sys
import sqlite3
import seq
import conf
if conf.usecython:
    import cnode as node
else:
    import node
from get_ncbi_ids_for_names import get_taxid_for_name 
from get_ncbi_tax_tree_no_species import get_all_included,clean_name

def construct_tree_only_ids(baseid,c,ids):
    species = []
    stack = []
    done = set()
    rt = None
    includelist = get_all_included(ids,c)

    # node_ids = {}  # id is key, value is parent id
    nodes = {}  # id is key, value is node
    stack.append(str(baseid))
    rt = node.Node()
    rt.label = baseid+"_"+str(baseid)
    rt.data["id"] = str(baseid)
    nodes[str(baseid)] = rt
    while len(stack) > 0:
        id = stack.pop()
        if id in done:
            continue
        done.add(id)
        c.execute("select ncbi_id,name,name_class,edited_name from taxonomy where parent_ncbi_id = ?",(id,))
        childs = []
        for j in c:
            tid = str(j[0])
            if includelist != None and tid not in includelist:
                continue
            childs.append(tid)
            stack.append(tid)
            if str(j[2]) == "scientific name":
                name = str(j[1])
                edname = str(j[3])
                nn = node.Node()
                nn.label = clean_name(name)#+"_"+str(tid)
                nn.data["id"] = tid
                nodes[tid] = nn
                # node_ids[tid] = id
                nn.parent = nodes[id]
                nodes[id].add_child(nn)
        if len(childs) == 0 and id not in species:
            species.append(id)
    for i in rt.iternodes():
        if len(i.children) == 0:
            continue
        else:
            i.label = ""
    going = True
    while going:
        found = False
        for i in rt.iternodes():
            if i.parent != None and len(i.children) == 1 and i.label == "":
                par = i.parent
                ch = i.children[0]
                par.remove_child(i)
                par.add_child(ch)
                found = True
                break
        if found == False:
            going = False
            break
    return rt


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python "+sys.argv[0]+" dbname baseid alnfile")
        sys.exit(0)

    dbname = sys.argv[1]
    baseid = sys.argv[2]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    ids = set()
    for i in seq.read_fasta_file_iter(sys.argv[3]):
        ids.add(get_taxid_for_name(c,i.name.replace("_"," ")))
    t = construct_tree_only_ids(baseid,c,ids)
    print(t.get_newick_repr(False)+";")
