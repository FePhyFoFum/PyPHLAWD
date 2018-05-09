---
layout: page
title: Other
permalink: /other/
---
## Finding good clusters

There is a script that can be useful for finding good clusters to use for concatenation. A user can always check the `info.html` or investigate specific clusters, but there are times that you might want to try and automate the discovery of good clusters. The script is run with the command `python src/find_good_clusters_for_concat.py startdir`. The `startdir` refers to the directory that you created with the PyPHLAWD analysis. This script will check for clusters that have at least a certain proportion of taxa represented based on the number in NCBI (the `cluster_prop` in `conf.py`) and at least a certain size (the `smallest_cluster` in `conf.py`). This checks from tip to root so if there is a genus that has good representation for a gene, it will include that even if it doesn't have good representation in the deeper clade. Here is a demonstration of the script from the [clustering example](https://fephyfofum.github.io/PyPHLAWD/runs/clustering_ex/).

![clusters]({{ site.url }}/PyPHLAWD/assets/img/clus_ex_3.gif)


## Using your own sequences

**Coming soon!** The idea here is to be able to either supplement the NCBI sequences or to conduct your own analysis entirely of your own sequences. To do this, you will still want to create your own database of the sequences using the table structure already in use with the `phlawd_db_maker`. 

To add your own sequences to an analysis, regardless of whether they are supplemental or not, you will want to add your sequences to the database. You can have this data in two forms: one file per taxon with sequence data in a fasta format in that file or one file with format `>taxon_name@seq_id`. 