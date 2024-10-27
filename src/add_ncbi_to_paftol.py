import sys
import sqlite3
import tree_reader
import conf
if conf.usecython:
    import cnode as node
else:
    import node as node   

from get_ncbi_ids_for_names import get_taxid_for_name_limit_left_right


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"paftol db")
        sys.exit(0)
    pft = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    dbname = sys.argv[2]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    left = 0
    right = 0
    c.execute("select left_value,right_value from taxonomy where name = 'Viridiplantae';")
    for i in c:
        left = str(i[0])
        right = str(i[1])
    for i in pft.leaves():
        genus = i.label.split("_")[-1]
        a = get_taxid_for_name_limit_left_right(c,genus,left,right)
        if a == None:
            i.label += "_NOVALUE"
        else:
            i.label += "_"+a
    c.close()
    print(pft.get_newick_repr(False)+";")