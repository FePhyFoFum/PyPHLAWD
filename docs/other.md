---
layout: page
title: Other
permalink: /other/
---
This page serves to describe some other information on particular analyses.

Topics

- [Finding good clusters](#finding-good-clusters)
- [Excluding taxa or sequences](#excluding-taxa-or-sequences)
- [Adding outgroups](#adding-outgroups)
- [Changing names on a tree](#changing-names-on-a-tree)
- [Tip-to-root clustering](#tip-to-root-clustering)
- [Using your own sequences](#using-your-own-sequences)

## Finding good clusters

There is a script that can be useful for finding good clusters to use for concatenation. A user can always check the `info.html` or investigate specific clusters, but there are times that you might want to try and automate the discovery of good clusters. The script is run with the command `python src/find_good_clusters_for_concat.py startdir`. The `startdir` refers to the directory that you created with the PyPHLAWD analysis. This script will check for clusters that have at least a certain proportion of taxa represented based on the number in NCBI (the `cluster_prop` in `conf.py`) and at least a certain size (the `smallest_cluster` in `conf.py`). This checks from tip to root so if there is a genus that has good representation for a gene, it will include that even if it doesn't have good representation in the deeper clade. Here is a demonstration of the script from the [clustering example](https://fephyfofum.github.io/PyPHLAWD/runs/clustering_ex/).

![clusters]({{ site.url }}/PyPHLAWD/assets/img/clus_ex_3.gif)

## Excluding taxa or sequences

PyPHLAWD allows you to exclude bad sequences or patterns that can be found in the sequence name or description. For example, in the `bad_taxa.py` users can place NCBI taxon ids and in `bad_seqs.py` users can place NCBI GenBank ids. IDs found in these files will be excluded during the analysis. There are already some placed in there that the user can delete or add to. In addition to these, there are also the files `exclude_patterns.py` and `exclude_desc_patterns.py`. In `exclude_patterns.py` you will find text that if found in the species name, it will be skipped. In `exclude_desc_patterns.py` you will find text that if found in the sequence description it will be skipped. The user can edit these as they like. 

## Adding outgroups

A script is included in the `src/` directory called `add_outgroup_to_matrix.py`. You can run this either like `python src/add_outgroup_to_matrix.py` or just directly `src/add_outgroup_to_matrix.py`. If you do not do it directly, autocomplete may not work (feel free to post an issue if this is a problem as there are some simple solutions). This has specific arguments including:

```
usage: add_outgroup_to_matrix.py [-h] -b DATABASE -m MATRIX -p PARTS -t TAXON
                                 -o OUTPREFIX [-mn MINOVERLAP] [-mx MAXTAXA]

optional arguments:
  -h, --help            show this help message and exit
  -b DATABASE, --database DATABASE
                        Database with sequences. (default: None)
  -m MATRIX, --matrix MATRIX
                        Concatenated matrix probably from
                        find_good_clusters_for_concat.py (default: None)
  -p PARTS, --parts PARTS
                        The partition file probably from
                        find_good_clusters_for_concat.py (default: None)
  -t TAXON, --taxon TAXON
                        The taxon (use the NCBI taxon id) to add. (default:
                        None)
  -o OUTPREFIX, --outprefix OUTPREFIX
                        The output file prefix. (default: None)
  -mn MINOVERLAP, --minoverlap MINOVERLAP
  -mx MAXTAXA, --maxtaxa MAXTAXA
```

The `-b` is just the regular database. The `-m` would be the matrix from `find_good_clusters_for_concat.py` (or actually any matirx will work as long as it is in fasta aligned format). The `-p` would be the partition file formatted for RAxML. The `-t` should be the NCBI taxon id. The `-o` will be the outfile prefix. `-mn` is the minimum number of genes that are required to overlap. This will always favor those with more genes represented per taxon. The `mx` is the maximum number of taxa to add. You can run the script as many times as you like to add more outgroups like this

```
src/add_outgroup_to_matrix.py -b pln.05292018.db -m Adoxaceae_4206/Adoxaceae_4206_outaln -p Adoxaceae_4206/Adoxaceae_4206_outpart -t 49606 -o AdoxOut1 -mx 5 -mn 2
src/add_outgroup_to_matrix.py -b pln.05292018.db -m AdoxOut1.outaln -p AdoxOut1.outpart -t 19952 -o AdoxOut2 -mx 5 -mn 2
```

In each case, a file called `AdoxOut1.table` and `AdoxOut2.table` will be produced that have the sequences that were included. 

## Changing names on a tree

There are several ways to change names on the tree from ncbi to real names. The one that I find the most convenient is using the script `change_ncbi_to_name_tre_fromurl.py`. This uses a webservice and I happen to have one running. You can use it as below where the tip names are taxon ids from ncbi.

```
python src/change_ncbi_to_name_tre_fromurl.py http://141.211.236.35:10999 RAxML_bestTree.AdoxOut2 > RAxML_bestTree.AdoxOut2.cn
```

## Tip-to-root clustering

PyPHLAWD uses a tip-to-root clustering process that works to identify orthologous sequences based upon previously determined phylogenetic relationships. In the case of PyPHLAWD the taxonomy as input on NCBI is used for this. Initial clusters are formed at the tips through an all-by-all blast approach (user specified settings), followed by a Markov clustering approach as implemented in MCL. The sequences are then aligned using mafft and this process is performed for every tip. The tips are then combined in a postorder fashion (tip-to-root). PyPHLAWD selects the longest sequence from a tip cluster and compares that to its closest related sister cluster as identified through the NCBI taxonomy.

## Using your own sequences

**Coming soon!** The idea here is to be able to either supplement the NCBI sequences or to conduct your own analysis entirely of your own sequences. To do this, you will still want to create your own database of the sequences using the table structure already in use with the `phlawd_db_maker`. 

To add your own sequences to an analysis, regardless of whether they are supplemental or not, you will want to add your sequences to the database. You can have this data in two forms: one file per taxon with sequence data in a fasta format in that file or one file with format `>taxon_name@seq_id`. 
