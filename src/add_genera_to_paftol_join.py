import sys
import os

import tree_reader

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python",sys.argv[0],"paftoljoin dir")
        sys.exit(0)
    t1 = tree_reader.read_tree_file_iter(sys.argv[1]).__next__()
    dir = sys.argv[2]
    if dir[-1] != "/":
        dir += "/"
    for o in os.listdir(dir):
        print(o,file=sys.stderr)
        gn = o.split("_")[0]
        t2 = tree_reader.read_tree_file_iter(dir+"/"+o).__next__()
        for i in t1.iternodes():
            if i.label.split("_")[-1] == gn:
                par = i.parent
                par.remove_child(i)
                par.add_child(t2)
                break
    print(t1.get_newick_repr(False)+";")
