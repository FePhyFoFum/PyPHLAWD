---
layout: page
title: Introduction
permalink: /introduction/
---

## About
PyPHLAWD is an updated version of [PHLAWD](https://github.com/blackrim/phlawd) written in python. This version uses the tip-to-root clustering method as a basis for identifying orthology to assemble large phylogenetic trees. Many of the scripts in PyPHLAWD may be run separately 
allowing the functions of the program to be performed without requiring the full analysis. As such their functions have been outlined under th scripts tab.

### Tip-to-root clustering
This process works to identify orthologous sequences based upon previously determined phylogenetic relationships. In the case of PyPHLAWD the taxonomy
as input on ncbi is used for this. Initial clusters are formed at the tips through an all-by-all blast approach (user specified settings), followed by a Markov clustering 
approach as implemented in MCL. The sequences are then aligned using MAFFT and this process is performed for every tip. The tips are then combined in a
postorder fashion (tip-to-root). PyPHLAWD selects the longest sequence from a tip cluster and compares that to its closest related sister cluster as identified
through the NCBI taxonomy.   

