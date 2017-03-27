import os
import sys
import seq
from shutil import copyfile
from logger import Logger
from conf import nthread

nthread = str(nthread)

import platform
plat = platform.platform()
mac = False
if "Darwin" in plat:
    mac = True

alc = "mafft --thread "+nthread+" --adjustdirection --quiet INFILE 2> mafft.out > OUTFILE "
trf = "FastTree -nt -gtr INFILE 2>fasttree.out > OUTFILE"
treemake = True

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print "python "+sys.argv[0]+" startdir [logfile]"
        sys.exit(0)
    dirr = sys.argv[1]
    LOGFILE = "pyphlawd.log"
    if len(sys.argv) == 3:
        LOGFILE = sys.argv[2]
    log = Logger(LOGFILE)
    log.a()
    for i in os.listdir(dirr):
        if ".fa" in i:
            inf = dirr+"/"+i
            ouf = dirr+"/"+i.replace(".fa",".aln")
            sc = 0
            for j in seq.read_fasta_file_iter(inf):
                sc += 1
            if sc > 1:
                log.w("ALIGNING FROM "+inf+" TO "+ouf)
                os.system(alc.replace("INFILE",inf).replace("OUTFILE",ouf))
                if mac == False:
                    os.system("sed -i 's/_R_//g' "+ouf)
                else:
                    os.system("sed -i '' 's/_R_//g' "+ouf)
                if sc > 3 and treemake:
                    log.w("TREE BUILDING FROM "+ouf+" TO "+ouf.replace(".aln",".tre"))
                    os.system(trf.replace("INFILE",ouf).replace("OUTFILE",ouf.replace(".aln",".tre")))
            else:
                log.w("COPYING FROM "+inf+" TO "+ouf)
                copyfile(inf,ouf)
    log.c()
