

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def escape_space(ins):
    return ins.replace(" ","\ ")

def newick_name(lab):
    invalidchars = ":;[](),'"
    if any(elem in lab for elem in invalidchars):
        print("gotta quote this sucka: " + lab)
        lab = "'" + lab + "'"
    else:
        lab = lab.replace(" ","_")
    return (lab)
