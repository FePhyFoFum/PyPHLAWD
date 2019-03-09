#!/usr/bin/python

import argparse
import sys
import sqlite3
import conf
if conf.usecython:
    import cnode as node
else:
    import node

def clean_name(name):
    return name.replace(" ", "_").replace("&","_").replace(":","_")

def get_all_included(taxalist,c):
    inc = set()
    for i in taxalist:
        cur = str(i)
        going = True
        while going:
            c.execute("select ncbi_id, parent_ncbi_id from taxonomy where ncbi_id = ?", (cur, ))
            count = 0
            for j in c:
                count += 1
                inc.add(str(j[0]))
                par = str(j[1])
                if par != "1" and par not in inc:
                    cur = par
                else:
                    going = False
                    break
            if count == 0:
                print("delete "+i)
    return inc

def construct_tree(taxon, db, includespecies, taxalist = None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    includelist = None
    if taxalist != None:
        tl = set()
        tlf = open(taxalist,"r")
        for i in tlf:
            tl.add(i)
        tlf.close()
        includelist = get_all_included(tl,c)
    species = []
    stack = []
    done = set()
    rt = None
    nodes = {}  # id is key, value is node
    if (taxon.isdigit()):
        c.execute("select ncbi_id from taxonomy where ncbi_id = ?", (taxon, ))
    else:
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
        if includespecies:
            c.execute("select ncbi_id,name,name_class,edited_name from taxonomy where parent_ncbi_id = ?",(id,))
        else:
            c.execute("select ncbi_id,name,name_class,edited_name from taxonomy where parent_ncbi_id = ? and node_rank != 'species'",(id,))
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
                nn.label = clean_name(edname)+"_"+str(tid)
                nn.data["id"] = tid
                nodes[tid] = nn
                nn.parent = nodes[id]
                nodes[id].add_child(nn)
        if len(childs) == 0 and id not in species:
            species.append(id)
    return rt


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--taxon", help="Taxon constituting root node of tree (name or id)",
                        required=True)
    parser.add_argument("-d", "--database", help="Location of database", required=True)
    parser.add_argument("-i", "--includespecies", help="Include terminal species in tree (default = False)",
                        action="store_true", required=False, default=False)
    parser.add_argument("-l", "--taxlistfile", help="File listing taxa to include (one per line)", required=False)
    parser.add_argument("-o", "--outfile", help="Output tree file", required=False)
    
    args = parser.parse_args()
    
    taxalist = None
    if args.taxlistfile:
        taxalist = args.taxlistfile
    
    tree = construct_tree(args.taxon, args.database, args.includespecies, taxalist)
    
    if args.outfile:
        outfile = open(args.outfile,"w")
        outfile.write(tree.get_newick_repr(False)+";\n")
    else:
        print(tree.get_newick_repr(False)+";")

