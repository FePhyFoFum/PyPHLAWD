import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "python "+sys.argv[0]+" blasttable barcodetable seqtable"
        sys.exit(0)
    inf = open(sys.argv[1],"r")
    
    barc = {}# key is seqid, value is list of qids
    barce = {} #key is seqid, value is e
    barci = {} #key is seqid, value is i
    barcl = {} #key is seqid, value is l
    ls = None
    lq = None
    lqs = None
    lqe = None
    lss = None
    lse = None
    for i in inf:
        spls = i.strip().split()
        s = spls[0]
        q = spls[2]
        if s == q:
            continue
        if s not in barc:
            barc[s] = []
            barci[s] = []
            barce[s] = []
            barcl[s] = []
        i = float(spls[4])
        qs = int(spls[7])
        qe = int(spls[8])
        if qs > qe:
            t = qs
            qs = qe
            qe = t
        ss = int(spls[9])
        se = int(spls[10])
        if ss > se:
            t = ss
            ss = se
            se = t
        if ls == s and lq == q:
            lqs += qs
            lqe += qe
            lss += ss
            lse += se
            continue # not taking double hits
        else:
            ls = s
            lq = q
            lqs = qs
            lqe = qe
            lss = ss
            lse = se
        ev = float(spls[11])
        l = qe-qs
        barc[s].append(q)
        barci[s].append(i)
        barce[s].append(ev)
        barcl[s].append(l)
    inf.close()
    
    barcf = open(sys.argv[2],"r")
    barcodes = []
    barcodes_name = {}
    for i in barcf:
        spls = i.strip().split("\t")
        barcodes.append(spls[3])
        barcodes_name[spls[3]] = spls[4]
    barcf.close()

    barcf = open(sys.argv[3],"r")
    allcodes = []
    allcodes_name = {}
    for i in barcf:
        spls = i.strip().split("\t")
        allcodes.append(spls[3])
        allcodes_name[spls[3]] = spls[4]
    barcf.close()

    for i in barc:
        print i,barcodes_name[i]
        count = 0
        for j in barc[i]:
            e = barce[i][count]
            _i= barci[i][count]
            l = barcl[i][count]
            count += 1
            if j in barcodes:
                print "\t==",j,allcodes_name[j],e,_i,l
            else:
                print "\t",j,allcodes_name[j],e,_i,l
