#directory that houses the scripts for pyphlawd
DI = "~/Dropbox/programming/pyphlawd/src/"

#just a temporary name for the fasta files
tempname = "temp.fas"

#smallest seq size
smallest_size = 500

#sample size for blast and comps
dosamp = True
sampsize = 20

#number of threads for mafft and blast
nthread = 10

#take out taxon duplications
takeouttaxondups = True

#build trees during alignment making
treemake = False

#merge alignment
merge = True

#blast bits
length_limit = 0.65
evalue_limit = 10e-10
perc_identity = 20

#cutoffs for trim tips
relcut = 0.75
abscut = 1

#superfluous things
emoticons = True
