#directory that houses the scripts for pyphlawd
DI = "~/Dropbox/programming/pyphlawd/src/"
#don't edit, just adding a trailing / if it isn't there
if DI[-1] != "/":
    DI += "/"

py = "python3"

#just a temporary name for the fasta files
tempname = "temp.fas"

#smallest seq size
smallest_size = 450

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
evalue_limit_lc = 10e-20
perc_identity = 20

#bait cut
bait_cut = False
bait_cut_smallest_size = 300

#cutoffs for trim tips
relcut = 0.25
abscut = 0.7
abscutint = 1.5

#cutoffs for qjpost
qjfreqcut = 0.3
#freq to cut for a particular tip
qjsmallcut = 0.1 
#maximum proportion of tips to cut
qjpropcut = 0.05

#superfluous things
emoticons = True

#cython
usecython = True

#find good clusters things
smallest_cluster = 20
cluster_prop = 0.2

#filter name mismatch
filternamemismatch = False
