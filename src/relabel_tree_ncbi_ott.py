import sys
import tree_reader

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" tree relabeld")
        sys.exit(0)
    tree = next(tree_reader.read_tree_file_iter(sys.argv[1]))

    nms = {}
    of = open(sys.argv[2],"r")
    for i in of:
        spls = i.strip().split("\t")
        nms[spls[0]] = "ott"+spls[1]
    of.close()

    for i in tree.leaves():
        if i.label in nms:
            i.label = nms[i.label]

    print(tree.get_newick_repr(True)+";")
