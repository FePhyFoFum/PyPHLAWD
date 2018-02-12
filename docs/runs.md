---
layout: page
title: Runs
permalink: /runs/
---

This assumes that you have already setup things as per the [installation instructions](https://fephyfofum.github.io/PyPHLAWD/install/).

## Running 
There are two basic ways to run PyPHLAWD (the outdir must exist):
- `python setup_clade.py Dipsacales PHLAWD_DBS/pln.db OUTDIR/`
- `python setup_clade_bait.py Dipsacales bait_dir/ PHLAWD_DBS/pln.db OUTDIR/`

### conf.py
There is a configuration file that has some basic configuration settings. You will probably need to at least change the `DI` setting. This is the location of the PyPHLAWD scripts that you downloaded. The other settings are described below. 

```
DI = "~/Dropbox/programming/pyphlawd/src/"     # location of the scripts
tempname = "temp.fas"    # the name of a temp file, created in your current dir
dosamp = True            # do you want to sample big seq files. If not, set `False`
sampsize = 20            # if True above, then set a size - the number of sequences
nthread = 10             # number of threads for threaded packages
treemake = False         # do you want to build trees for clusters? runtime increases
length_limit = 0.5       # seqs must match at least this length
evalue_limit = 10e-10    # evalue limit, must be better
perc_identity = 20       # at least this identity
```

If you edit this file, be sure to save your copy before you `git pull` as it will overwrite. There will soon be a way to identify which `conf.py` file you would like to use as an environmental variable (coming soon).

#### Changing parameters
 - `length_limit` : Typically, this works best if it is above 0.4. If you go too low, you may not that there are alignments problems (`PyPHLAWD` shouts in <font color="red"> RED CAPS </font>)
 - `perc_identity` : This also works best if it is not too low (as with `length_limit`) for the same reasons.
 - `evalue_limit` : This value you can gauge based on your typical usage with blast. For nucleotide sequences, we often use `10e-10` and for protein `10e-4`. However, there are no great rules (see [Smith and Pease 2017](https://academic.oup.com/bib/article/18/3/451/2453289) ) for some discussion.

### Clustering runs
Clustering runs use both `blast` and `mcl` to cluster sequences. They can also break clusters by trees as in Yang and Smith 2014 and Yang et al. 2015 but this hasn't been necessary yet with testing and so it is turned off by default. To run a clustering run you run `python setup_clade.py Dipsacales PHLAWD_DBS/pln.db OUTDIR/` where `Dipsacales` is the name in NCBI, `PHLAWD_DBS/pln.db` is where ever the relevant database is that was made with `phlawd_db_maker`, and `OUTDIR/` is where ever you want the resulting directory to be.

### Bait runs
In addition to the clustering runs (that will look at all the available data, you can also look at only the gene regions you're interest in (as the old PHLAWD).

#### Bait files
Bait files need to be in a directory and need to have the file ending `.fa` or `.fas` or `.fasta` and need to be fasta files. This requirement is necessary in order to recognize which files are intended to be the bait in the directory (so you can have other files in the directory).

### Subsetting taxa
With either of the above runs types, you can limit what taxa are considered. For this, you will need a file that has an ncbi id on each line. These will be the only ones considered. Then you run like:
- `python setup_clade.py Dipsacales PHLAWD_DBS/pln.db OUTDIR/ taxalist` 
- `python setup_clade_bait.py Dipsacales bait_dir/ PHLAWD_DBS/pln.db OUTDIR/ taxalist` 

There is a helper script that will help make your taxa list file. If you have a file that has `Genus species` on each line, you can use the script 
- `python get_ncbi_ids_for_names.py names_file PHLAWD_DBS/pln.db > taxalist`

### Updating analyses
Soon you will be able to add sequences to these runs without completely redoing all the analyses.
Coming soon!

## Output
PyPHLAWD will make a bunch of directories. In each directory, there will be a `clusters` folder that has either the constructed bait files or the clusters. There is also an `info.html` file in each directory. If you open the root one (the one inside the main directory made) you will see the stats for each cluster/bait that has more than 3 taxa. There will be an alignment file (with `.aln` file ending for each file) and a `.tre` if you have treemake on.

## Runtime considerations 
There are a number of things that can make the runtime shorter. The first is to do baited analyses. 