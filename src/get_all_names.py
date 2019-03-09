import sys
import tree_reader
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python "+sys.argv[0]+" infile")
        sys.exit(0)
    for i in tree_reader.read_tree_file_iter(sys.argv[1]):
        for j in i.iternodes():
            if len(j.label) > 0:
                if "ott" not in j.label:
                    print(j.label)
                else:
                    print(j.label)

