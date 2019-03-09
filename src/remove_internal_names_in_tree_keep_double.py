import tree_reader
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" infile outfile")
        sys.exit()
    tree = next(tree_reader.read_tree_file_iter(sys.argv[1]))
    for i in tree.iternodes():
        if len(i.children) == 0:
            continue
        if len(i.label) > 0:
            try:
                float(i.label)
            except:
                i.label = ""
    outf = open(sys.argv[2],"w")
    outf.write(tree.get_newick_repr(True)+";")
    outf.close()
