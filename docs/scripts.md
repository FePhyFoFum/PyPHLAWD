---
layout: page
title: Scripts
permalink: /scripts/
---
## Scripts

PyPHLAWD contains many scripts, and most of them can be run independently. Below is a list of some of the scripts and their functionality.

### Main Programs

- `setup_clade.py` This is the main program and will execute the clustering analysis. To run you will need to specify your clade of
interest, a database as downloaded by [phlawd_db_maker](https://github.com/blackrim/phlawd_db_maker), and a premade outdirectory
for the outputs of the analysis to be placed in.

EX: `python setup_clade.py CLADE PHLAWD_DB.db OUTDIR/`

- `setup_bait_clade.py` This runs the same analysis as `setup_clade.py`, however, it allows you to provide your own bait sequences.
These sequences should be in fasta format and put in a directory. If the sequences you have are not in fasta format, the program
`pxs2fa` from the suite [phyx](https://github.com/FePhyFoFum/phyx) can be used to convert it.

EX: `python setup_clade.py CLADE BAIT_DIR/ PHLAWD_DB.db OUTDIR/`

### Other Scripts

- `align_tip_clusters.py` This will align fasta sequences within a folder using [mafft](http://mafft.cbrc.jp/alignment/software/) and the [phyx](https://github.com/FePhyFoFum/phyx) program `pxssort`. This is good to run before
`add_clade_cluster.py` if the sequences have not been aligned.

EX: `python add_clade_cluster.py FOLDER_WITH_FASTA OPTIONAL_LOGFILE`

- `add_clade_cluster.py` This will run during the main program or can be run separately to combine clusters together. The user specifies
a folder with clusters to combine. This should contain a set of fasta files that end in `.fa` and their corresponding alignments ending
in `.aln`. The user can also specify a log file or alternatively the logfile `pyphlawd.log` will have the information written to.

EX: `python add_clade_cluster.py CLUSTER_FOLDER OUT_FOLDER OPTIONAL_LOGFILE`

- `change_id_to_name_fasta.py ` This will allow you to change names in a user input fasta file with a list of given names. The input is
a tab delimited file containing the current names in the first column and the names to be replaced with in the second.

EX: `python change_id_to_name_fasta.py Table.tsv InputFasta.fa OutputFile`

- `change_ncbi_to_name_tre_fromlist.py` Change the names on a tree. This will allow you to switch the names from ncbi to species file.
The table should be tab delimited.

EX: `python change_ncbi_to_name_tre_fromlist.py Table.tsv Tree.tre OutTree.tre`

- `compile_cython.sh` If you plan on using [cython](https://pypi.python.org/pypi/Cython/) while running PyPHLAWD, this program will set it
up to make the possible.

EX: `bash compile_cython.sh`

- `cut_long_internal_branches.py` This program will allow the user to split clades connect by a branch of a designated length. This is intended to divide clusters that have brought together based upon misidentified orthology. The user specifies a branch length cutoff and the number of taxa for a clade. The input will be a folder containing the trees that are to be cut and the file ending of those trees (e.g .new, .tre etc...).

EX: `python cut_long_internal_branches.py DIR_WITH_TREES TREEFILE_ENDING BRANCH_CUTOFF MIN_TAXA OUTDIR OPTIONAL_LOGFILE`

- `filter_blast.py` This program will create an mcl file out of a blast output.

EX: `python filter_blast.py BLASTOUTPUT MCLFILE`

- `get_all_ncbi_names.py` This is a script that will read all the names from your database and output a table with them. This is useful if you want to quickly see if species of interest are available. The table can be input to the name changing program `change_id_to_name_fasta.py` or `change_ncbi_to_name_tre_fromlist.py` in order to change ncbi names to species names.

EX: `python get_all_ncbi_names.py Database.db OutputFileName`

- `get_len_seq_summary.py` This program will summarize the length to standard out of every fasta sequence in a file.

EX: `python get_len_seq_summary.py FASTA`

- `trim_tips.py` This program is designed to help clean trees after they have been inferred. You specify an absolute value and a relative value for which terminal branches of these lengths will be removed. This is to help remove sequences that have been included from misidentified orthology, long branch attraction or another source of systematic error. Details regarding choice for absolute and relative values may be found in Yang and Smith, 2014. This is performed during the regular analysis with the absolute and relative values specified in the `conf.py` file, however, can also be used for refinement of final trees.

EX: `python trim_tips.py TREE.tre REL_VALUE ABS_VALUE`

- `write_fasta_files_from_mcl.py` This program is designed to extract the clusters identified through markov clustering as implemented in 
[mcl](https://micans.org/mcl/). The input is a fasta file which contains all sequences clustered (typically the file which an all-by-all blast was performed
on), the outfile from the clustering analysis and the minimal number of required to be in the clustering analysis. This program requires a
premade folder, and the output will be all the clusters identified by mcl that meet the minimum number of taxa requirement.

EX: `python write_fasta_files_from_mcl.py AllFasta.fa mcl_outfile minimum_taxa OUTDIR`


