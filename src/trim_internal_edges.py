import sys
import tree_reader

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python "+sys.argv[0]+" infile.tre cutoff")
        sys.exit(0)
    cutoff = float(sys.argv[2])
    tree = next(tree_reader.read_tree_file_iter(sys.argv[1]))
    remove = set()
    rootlvs = set(tree.lvsnms())
    for i in tree.iternodes():
        if i.length > cutoff:
            tips = set(i.lvsnms())
            others = rootlvs-tips
            if others < tips:
                for j in list(others):
                    remove.add(j)
            else:
                for j in list(tips):
                    remove.add(j)
    for i in remove:
        print("removing:",i, file=sys.stderr)