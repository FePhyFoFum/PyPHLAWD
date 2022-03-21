import sys
import ftplib
import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--gzfilesdir",help="Where are the gzfiles",required=True)
    parser.add_argument("-d","--div",help="Which division (pln, etc)?",default="pln",required=True)

    if len(sys.argv[1:]) == 0:
        sys.argv.append("-h")
    args = parser.parse_args()

    GBFTP = "ftp.ncbi.nih.gov"
    ftp = ftplib.FTP(GBFTP)
    ftp.login("anonymous", "anonymous")
    ftp.cwd("genbank")
    files = ftp.nlst("")
    ftp.close()

    kf = [i for i in files if "gb"+args.div in i]
    #print(kf)
    fd = args.gzfilesdir
    if fd[-1] != "/":
        fd += "/"
    for i in os.listdir(fd):
        if i in kf:
            kf.remove(i)
    print(len(kf),"files to get")
    count = 1
    for i in kf:
        GBFTP = "ftp.ncbi.nih.gov"
        ftp = ftplib.FTP(GBFTP)
        ftp.login("anonymous", "anonymous")
        ftp.cwd("genbank")
        print(i,count,"of",len(kf))
        with open(fd+i, 'wb') as f:
            ftp.retrbinary('RETR ' + i, f.write)
        ftp.close() 
        count += 1
