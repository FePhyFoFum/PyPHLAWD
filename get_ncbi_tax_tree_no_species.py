import sys
import sqlite3
import node

def clean_name(name):
    return name.replace(" ", "_")

def construct_tree(taxon, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    species = []
    stack = []
    done = set()
    rt = None
    # node_ids = {}  # id is key, value is parent id
    nodes = {}  # id is key, value is node
    c.execute("select ncbi_id from taxonomy where name = ? and node_rank != 'species'", (taxon, ))
    for j in c:
        stack.append(str(j[0]))
        rt = node.Node()
        rt.label = taxon+"_"+str(j[0])
        rt.data["id"] = str(j[0])
        nodes[str(j[0])] = rt
    while len(stack) > 0:
        id = stack.pop()
        if id in done:
            continue
        done.add(id)
        c.execute("select ncbi_id,name,name_class from taxonomy where parent_ncbi_id = ? and node_rank != 'species'",(id,))
        childs = []
        for j in c:
            tid = str(j[0])
            childs.append(tid)
            stack.append(tid)
            if str(j[2]) == "scientific name":
                name = str(j[1])
                nn = node.Node()
                nn.label = clean_name(name)+"_"+str(tid)
                nn.data["id"] = tid
                nodes[tid] = nn
                # node_ids[tid] = id
                nn.parent = nodes[id]
                nodes[id].add_child(nn)
        if len(childs) == 0 and id not in species:
            species.append(id)
    return rt


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python "+sys.argv[0]+" taxon db"
        sys.exit(0)
    taxon = sys.argv[1]
    DB = sys.argv[2]
    tree = construct_tree(taxon, DB)
    print tree.get_newick_repr(False)+";"
