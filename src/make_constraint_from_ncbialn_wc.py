import sys
import sqlite3
import seq
import conf
if conf.usecython:
    import cnode as node
else:
    import node as node       
from get_ncbi_ids_for_names import get_taxid_for_name 
from get_ncbi_tax_tree_no_species import get_all_included,clean_name

noinclude = False
stopat = "genus"
useonly = False
useonlylist = ["family","subfamily"]

# may need to add teh custom parent bit
def get_all_included_wc(taxalist,c):
    inc = set()
    for i in taxalist:
        cur = str(i)
        going = True
        while going:
            if "_sm" in cur or "-" in cur:
                c.execute("select ncbi_id, parent_ncbi_id, custom_id,custom_parent_id from taxonomy where custom_id = ?", (cur, ))
            else:
                c.execute("select ncbi_id, parent_ncbi_id from taxonomy where ncbi_id = ?", (cur, ))
            count = 0
            for j in c:
                #print(j)
                count += 1
                if len(j) > 2:
                    if j[2] != None:
                        inc.add(str(j[2]))
                    else:
                        inc.add(str(j[0]))
                else:
                    inc.add(str(j[0]))
                if len(j) > 2:
                    if j[3] != None:
                        par = str(j[3])
                    else:
                        par = str(j[1])
                else:
                    par = str(j[1])
                if par != "1" and par not in inc:
                    cur = par
                else:
                    going = False
                    break
            if count == 0:
                print("delete "+i)
    return inc

# will need to continue to check this. 
def construct_tree_only_ids(baseid,c,ids):
    species = []
    stack = []
    done = set()
    rt = None
    includelist = get_all_included_wc(ids,c)
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
        if "_sm" in id or "-" in id: #in which case it is a wcid
            c.execute("select ncbi_id,name_class,name,node_rank,custom_id,custom_parent_id,custom_name from taxonomy where name_class = 'scientific name' and custom_parent_id = ?",(id,))
        else:
            c.execute("select ncbi_id,name_class,name,node_rank,custom_id,custom_parent_id,custom_name from taxonomy where name_class = 'scientific name' and parent_ncbi_id = ?",(id,))
        for j in c:
            tid = str(j[0])
            if j[4] != None:
                tid = str(j[4])
            #print(j,tid in includelist)
            if includelist != None and tid not in includelist:
                continue
            if tid in nodes:
                continue
            stack.append(tid)
            if str(j[1]) == "scientific name" and (noinclude == False or str(j[3]) != stopat):
                nn = node.Node()
                nn.label = str(tid)
                nn.data["id"] = tid
                nn.data["rank"] = str(j[3])
                nodes[tid] = nn
                # node_ids[tid] = id
                if id in ids or "incertae" in str(j[2]) or "unidentified" in str(j[2]) or "unplaced" in str(j[2]):
                    #should lose these and not constrain
                    nodes[tid] = nodes[id]
                    #nn.parent = nodes[id].parent
                    #nodes[id].parent.add_child(nn)
                else:
                    nn.parent = nodes[id]
                    nodes[id].add_child(nn)
            elif (noinclude == True and str(j[3]) == stopat) and str(j[1]) == "scientific name":
                if id in ids:
                    nodes[tid] = nodes[id].parent
                else:
                    nodes[tid] = nodes[id]
    if useonly: #remove any constraint that insn't in the list
        toremove = set()
        for i in rt.iternodes():
            if len(i.children) == 0 or i == rt:
                continue
            else:
                if i.data["rank"] not in useonlylist:
                    toremove.add(i)
        for i in toremove:
            p = i.parent
            if p == None:
                continue
            p.remove_child(i)
            i.parent = None
            for j in i.children:
                p.add_child(j)
                j.parent = p
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
    if len(rt.children) == 1:
        rt = rt.children[0]
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
        ids.add(i.name)
    t = construct_tree_only_ids(baseid,c,ids)
    print(t.get_newick_repr(False)+";")
