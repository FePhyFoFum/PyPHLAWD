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

## Changing names on a tree

## Tip-to-root clustering

PyPHLAWD uses a tip-to-root clustering process that works to identify orthologous sequences based upon previously determined phylogenetic relationships. In the case of PyPHLAWD the taxonomy as input on NCBI is used for this. Initial clusters are formed at the tips through an all-by-all blast approach (user specified settings), followed by a Markov clustering approach as implemented in MCL. The sequences are then aligned using mafft and this process is performed for every tip. The tips are then combined in a postorder fashion (tip-to-root). PyPHLAWD selects the longest sequence from a tip cluster and compares that to its closest related sister cluster as identified through the NCBI taxonomy.

## Using your own sequences

**Coming soon!** The idea here is to be able to either supplement the NCBI sequences or to conduct your own analysis entirely of your own sequences. To do this, you will still want to create your own database of the sequences using the table structure already in use with the `phlawd_db_maker`. 

To add your own sequences to an analysis, regardless of whether they are supplemental or not, you will want to add your sequences to the database. You can have this data in two forms: one file per taxon with sequence data in a fasta format in that file or one file with format `>taxon_name@seq_id`. 
