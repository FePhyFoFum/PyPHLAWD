#!/usr/bin/env python2

import argparse
import os
import random
import subprocess
import tree_reader
import tree_utils
import sys
import time
import math
import seq
import conf
if conf.usecython:
    from cnode import Node
else:
    from node import Node
from multiprocessing import Manager, Pool

"""Consider each node N in the rooted tree to identify bipartition X, which is
represented in the tree as the outgoing edge connecting N to its parent M. In a
fully bifurcating tree, the nodes N and M will each have two other connected
edges, which connect the nodes A and B to N, and C and D to M. If we unroot the
tree, then the bipartition X can be written as X = {A,B}|{C,D}, and the
branch represented by X in the rooted tree can be represented as the internal
branch in a four-tip unrooted topology with tips T = {A, B, C, D}, with an
internal branch representing X, and each tip t_i in T corresponding to a set
of leaves S_i in the original tree.

We may then perform a number of replicated topology searches consisting of
randomly drawing one leaf s_j from each S_i, and record the maximum likelihood
for the three possible resolutions. To assess the support for
bipartition X in the original tree, we summarize the quartet topology
replicates, and calculate the ICA score for the internal branch that is
consistent with X.

Because likelihoods are essentially not meaningful when there is no data
overlap, this has the option of requiring overlap between the four taxa.
"""

_title = "Estimate quartet jackknife ICA support on a tree with alts"

DEFAULT_RAXML = "raxml"
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR

PAUP = False

# this is the proportion of possible quartets that will be searched by the
# random quartet generation procedure before the procedure gives up. prevents
# long search times, randomly generating quartets when all of them are bad
DEFAULT_MAX_RANDOM_SAMPLE_PROPORTION = 0.5
max_random_sample_proportion = DEFAULT_MAX_RANDOM_SAMPLE_PROPORTION

# if the number of quartets requested is more than this proportion of the
# total possible number of quartets, then random generation procedure will
# not be used. instead, *all* quartets will be generated and number requested
# will be randomly drawn from them. prevents endless searching through randomly
# generated duplicates
# should probably *not* have this be a user-settable option
MAX_QUARTET_ENUMERATION_THRESHOLD = 0.333333

LNLIKETHRESH = 0  # -2lnlike
test_treefile = "test.trees"
test_trees = {0: "(L1,L2,(R1,R2));", 1: "(L1,R1,(L2,R2));",
              2: "(L1,R2,(L2,R1));"}

tree_counts = {0: 0, 1: 0, 2: 0}

tree_counts_detailed = 0

# this is for the data overlap check
alignment_data = {}  # key taxa,value set(sites)
check_overlap = False
DEFAULT_MIN_OVERLAP = 0
min_overlap = DEFAULT_MIN_OVERLAP
# min_overlap_loop = 100 # DISABLED, using different method
temp_wd = os.path.abspath("temp")


def write_figtree(outfname, intree):
    # change the names (internal only) to be the full figtree style label
    for i in intree.iternodes():
        if "freq" not in i.data:
            continue
        if len(i.children) == 0:
            continue
        freq = i.data["freq"]
        ica = i.data["ica"]
        qs_sc = i.data["qs_score"]
        qs_fr = i.data["qs_freq"]
        lab = i.label
        i.data["lab"] = lab  # so we can use it later
        rep = i.data["replicates"]
        if len(freq) > 0:
            lab = "[&label="+lab+",freq="+freq+",ica="+ica+",reps="+rep+",qs_score="+qs_sc+",qs_freq="+qs_fr+"]"
        else:
            lab = "[&label="+lab+",reps="+rep+",qs_score="+qs_sc+",qs_freq="+qs_fr+"]"
        i.label = lab
    outf = open(outfname, "w")
    outf.write('#NEXUS\nbegin trees;\n\n')
    outf.write('\ttree tree1 = [&R] ' + intree.get_newick_repr(True) + ";\n\n")
    outf.write('end;\n\n\n\nbegin figtree;\n\n\tset appearance.backgroundColour=#-1;\n\tset appearance.branchColorAttribute="freq";\n\tset appearance.branchLineWidth=1.0;\n\tset appearance.foregroundColour=#-16777216;\n\tset appearance.selectionColour=#-2144520576;\n\tset branchLabels.displayAttribute="Branch times";\n\tset branchLabels.fontName="sansserif";\n\tset branchLabels.fontSize=8;\n\tset branchLabels.fontStyle=0;\n\tset branchLabels.isShown=false;\n\tset branchLabels.significantDigits=4;\n\tset layout.expansion=0;\n\tset layout.layoutType="RECTILINEAR";\n\tset layout.zoom=0;\n\tset nodeBars.barWidth=4.0;\n\tset nodeLabels.displayAttribute="label";\n\tset nodeLabels.fontName="sansserif";\n\tset nodeLabels.fontSize=8;\n\tset nodeLabels.fontStyle=0;\n\tset nodeLabels.isShown=false;\n\tset nodeLabels.significantDigits=4;\n\tset polarLayout.alignTipLabels=false;\n\tset polarLayout.angularRange=0;\n\tset polarLayout.rootAngle=0;\n\tset polarLayout.rootLength=100;\n\tset polarLayout.showRoot=true;\n\tset radialLayout.spread=0.0;\n\tset rectilinearLayout.alignTipLabels=false;\n\tset rectilinearLayout.curvature=0;\n\tset rectilinearLayout.rootLength=100;\n\tset scale.offsetAge=0.0;\n\tset scale.rootAge=1.0;\n\tset scale.scaleFactor=1.0;\n\tset scale.scaleRoot=false;\n\tset scaleAxis.automaticScale=true;\n\tset scaleAxis.fontSize=8.0;\n\tset scaleAxis.isShown=false;\n\tset scaleAxis.lineWidth=1.0;\n\tset scaleAxis.majorTicks=1.0;\n\tset scaleAxis.origin=0.0;\n\tset scaleAxis.reverseAxis=false;\n\tset scaleAxis.showGrid=true;\n\tset scaleAxis.significantDigits=4;\n\tset scaleBar.automaticScale=true;\n\tset scaleBar.fontSize=10.0;\n\tset scaleBar.isShown=true;\n\tset scaleBar.lineWidth=1.0;\n\tset scaleBar.scaleRange=0.0;\n\tset scaleBar.significantDigits=4;\n\tset tipLabels.displayAttribute="Names";\n\tset tipLabels.fontName="sansserif";\n\tset tipLabels.fontSize=8;\n\tset tipLabels.fontStyle=0;\n\tset tipLabels.isShown=true;\n\tset tipLabels.significantDigits=4;\n\tset trees.order=true;\n\tset trees.orderType="decreasing";\n\tset trees.rooting=false;\n\tset trees.rootingType="User Selection";\n\tset trees.transform=false;\n\tset trees.transformType="cladogram";\nend;\n\n')
    outf.close()
    for i in intree.iternodes():
        if "freq" not in i.data:
            continue
        if len(i.children) == 0:
            continue
        i.label = i.data["lab"]


def write_test_trees(temp_wd):
    s0 = "(L1,L2,(R1,R2));\n"
    s1 = "(L1,R1,(L2,R2));\n"
    s2 = "(L1,R2,(L2,R1));\n"
    test_trees = open(temp_wd + "/" + test_treefile+".0", "w")
    test_trees.write(s0)
    test_trees.close()
    test_trees = open(temp_wd + "/" + test_treefile+".1", "w")
    test_trees.write(s1)
    test_trees.close()
    test_trees = open(temp_wd + "/" + test_treefile+".2", "w")
    test_trees.write(s2)
    test_trees.close()


def record_overlap_for_tips(aln):
    for i in aln:
        sites = []
        for j in range(len(aln[i])):
            if aln[i][j] not in ["-", "?", "N", "n"]:
                sites.append(j)
        alignment_data[i] = set(sites)


def check_overlap_aln(names):
    passed = False
    names = list(names)
    intersect = set(alignment_data[names[0]])
    for n in names[1:]:
        intersect = intersect.intersection(alignment_data[n])
    if len(intersect) >= min_overlap:
        passed = True
    return passed


def process_replicate(replicate):
    os.chdir(temp_wd)

    # just alias dictionary elements for convenience
    queue = replicate["queue"]
    lock = replicate["lock"]
    using_partitions = replicate["using_partitions"]
    node_id = replicate["node_id"]
    replicate_id = replicate["replicate_id"]
    raxml_path = replicate["raxml_path"]
    all_seqs = replicate["seqs"]
    result = {}
    result["seqs_names"] = replicate["seqs_names"]
    """result["seq_labels"] = {}
    result["seq_labels"]["L"] = []
    result["seq_labels"]["R"] = []
        for x in range(1, 3):
            for y in all_seqs["L1"].keys():
                result["seq_labels"][w].append(w+str(x)+"_"+str(y))
    """

    # generate a label that will be unique within this run
    #  (but probably not among runs!)
    unique_label = node_id + "." + replicate_id

    # generate labels for temp files
    if using_partitions:
        # make a copy of the partitions file
        temp_part_fname = "temp_parts." + unique_label
        subprocess.call("cp temp_parts " + temp_part_fname, shell=True)

    temp_aln_fname = "temp_inseqs." + unique_label
    # temp_aln_test_read_label = "temp_read_aln." + unique_label
    temp_ml_search_label = "temp_tree_search." + unique_label

    # write the alignment
    with open(temp_aln_fname, "w") as outfile:
        for l in all_seqs:
            outfile.write(">" + l + "\n" + all_seqs[l] + "\n")

    # this will test the three topologies
    if LNLIKETHRESH > 0:
        # test alignment readability by raxml, also filters missing columns
        # removed, don't think this is necessary anymore
        # do the treesearch using the filtered data
        raxml_args = [raxml_path,
                      "-s", temp_aln_fname,
                      "-n", temp_ml_search_label+".0",
                      "-m", "GTRCAT",
                      "-T", "2",
                      "-p", "123",
                      "-f", "N",
                      "--silent",
                      "-z", "test.trees.0"]

        if using_partitions:
            raxml_args += ["-q", temp_part_fname]

        result["raxml_args"] = " ".join(raxml_args)
        if args.verbose:
             print(('\ncalling:\n\n' + result["raxml_args"] + '\n'))

        p = subprocess.Popen(raxml_args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ts, tse = p.communicate()
        result["raxml_stdout"] = ts.decode("utf-8")
        result["raxml_stderr"] = tse
        raxml_args = [raxml_path,
                      "-s", temp_aln_fname,
                      "-n", temp_ml_search_label+".1",
                      "-m", "GTRCAT",
                      "-T", "2",
                      "-p", "123",
                      "-f", "N",
                      "--silent",
                      "-z", "test.trees.1"]
        p = subprocess.Popen(raxml_args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ts, tse = p.communicate()
        result["raxml_stdout"] += ts.decode("utf-8")
        result["raxml_stderr"] += tse
        raxml_args = [raxml_path,
                      "-s", temp_aln_fname,
                      "-n", temp_ml_search_label+".2",
                      "-m", "GTRCAT",
                      "-T", "2",
                      "-p", "123",
                      "-f", "N",
                      "--silent",
                      "-z", "test.trees.2"]
        p = subprocess.Popen(raxml_args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ts, tse = p.communicate()
        result["raxml_stdout"] += ts.decode("utf-8")
        result["raxml_stderr"] += tse
    else:  # this will do the ML, seems more stable with RAxML, esp. small ones
        raxml_args = [raxml_path,
                      "-s", temp_aln_fname,
                      "-n", temp_ml_search_label,
                      "-m", "GTRCAT",
                      "-T", "2",
                      "-p", "123",
                      "--silent"]
        if using_partitions:
            raxml_args += ["-q", temp_part_fname]
        result["raxml_args"] = " ".join(raxml_args)
        if args.verbose:
             print(('\ncalling:\n\n' + result["raxml_args"] + '\n'))
        p = subprocess.Popen(raxml_args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ts, tse = p.communicate()
        result["raxml_stdout"] = ts.decode("utf-8")
        #print (result["raxml_stdout"])
        result["raxml_stderr"] = tse
    result["label"] = unique_label
    queue.put(result)
    # increment counter and update user feedback
    replicate["n_completed"].value += 1
    lock.acquire()
    sys.stdout.write("\r"+str(replicate["n_completed"].value) + " / " +
                     str(len(replicates)))
    sys.stdout.flush()
    lock.release()


def write_paup(fname, seqs):
    fn = open(fname, "w")
    slen = len(seqs["L1"])
    fn.write("#nexus\n")
    fn.write("begin data;\n")
    fn.write("  dimensions ntax=4 nchar="+str(slen)+";\n")
    fn.write("  format datatype=dna missing=-;\n")
    fn.write("  matrix\n")
    for l in seqs:
        fn.write("    " + l + " " + seqs[l] + "\n")
    fn.write("    ;\nend;\n\nbegin trees;\n")
    for l in range(3):
        fn.write("  utree t"+str(l)+" = "+test_trees[l]+";\n")
    fn.write("end;\n\n")
    fn.write("begin paup;\n")
    # fn.write("  lset lcollapse=no precision=double nst=6 rmatrix=estimate basefreq=empirical;\n")
    fn.write("  lset lcollapse=no precision=double nst=1 basefreq=equal;\n")
    fn.write("  lscores all /scorefile="+fname+".out replace=yes;\n")
    fn.write("  quit;\n")
    fn.write("end;\n")
    fn.close()


def process_replicate_paup(replicate):
    os.chdir(temp_wd)

    # just alias dictionary elements for convenience
    queue = replicate["queue"]
    lock = replicate["lock"]
    using_partitions = replicate["using_partitions"]
    node_id = replicate["node_id"]
    replicate_id = replicate["replicate_id"]
    raxml_path = replicate["raxml_path"]
    all_seqs = replicate["seqs"]
    result = {}
    result["seqs_names"] = replicate["seqs_names"]

    # generate a label that will be unique within this run
    #  (but probably not among runs!)
    unique_label = node_id + "." + replicate_id

    # generate labels for temp files
    if using_partitions:
        # make a copy of the partitions file
        temp_part_fname = "temp_parts." + unique_label
        subprocess.call("cp temp_parts " + temp_part_fname, shell=True)

    temp_aln_fname = "temp_inseqs." + unique_label
    # temp_aln_test_read_label = "temp_read_aln." + unique_label
    temp_ml_search_label = "temp_tree_search." + unique_label

    # write the alignment
    write_paup(temp_aln_fname, all_seqs)

    paup_args = ["paup", temp_aln_fname]
    # if using_partitions:
    #     raxml_args += ["-q", temp_part_fname]
    result["raxml_args"] = " ".join(paup_args)
    p = subprocess.Popen(paup_args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if args.verbose:
        print((result['raxml_args']))

    ts, tse = p.communicate()
    result["raxml_stdout"] = ts.decode("utf-8")
    result["raxml_stderr"] = tse
    result["label"] = unique_label
    queue.put(result)
    # increment counter and update user feedback
    replicate["n_completed"].value += 1
    lock.acquire()
    sys.stdout.write("\r"+str(replicate["n_completed"].value) + " / " +
                     str(len(replicates)))
    sys.stdout.flush()
    lock.release()


def process_raxml_info_2lk(raxml_info_file_path, verbose):
    treelike = {0: 0, 1: 0, 2: 0}
    smallest_b = False
    smallest = None
    smallest_int = None
    second_smallest = None
    correct = None
    next_best = None
    # with open(raxml_info_file_path+".0", "r") as info_result:
    resstr = raxml_info_file_path.split("\n")
    counter = 0
    counteron = False
    name = None
    for x in resstr:
        # print(x)
        if "temp_inseqs" in x:
            name = x.strip().split(" ")[2]
        if "test.trees.1" in x:
            counter = 1
        if "test.trees.2" in x:
            counter = 2
        if "Tree 0 Likelihood " in x:
            treelike[counter] = float(x.split(" ")[3])
        # print (treelike)
        smallest = treelike[0]
        smallest_int = 0
        correct = treelike[0]
        if treelike[1] > smallest:
            second_smallest = smallest
            smallest = treelike[1]
            smallest_int = 1
        else:
            second_smallest = treelike[1]
        if next_best is None:
            next_best = treelike[1]
        elif treelike[1] > next_best:
            next_best = treelike[1]
        if treelike[2] > smallest:
            second_smallest = smallest
            smallest = treelike[2]
            smallest_int = 2
        elif treelike[2] > second_smallest:
            second_smallest = treelike[2]
        if next_best is None:
            next_best = treelike[2]
        elif treelike[2] > next_best:
            next_best = treelike[2]
    if abs(smallest - second_smallest) > LNLIKETHRESH:
        smallest_b = True
    if verbose:
        print("---")
        print(name)
        print(treelike)
        print((smallest_int, smallest_b))
        print((test_trees[smallest_int]))
        print((correct, next_best, correct-next_best))
    return smallest_b, smallest_int, correct-next_best


def process_raxml_info_ML(raxml_tree_file_path, verbose):
    smallest_int = None
    t = open(raxml_tree_file_path, "r")
    ts = t.readline()
    t.close()
    restree = tree_reader.read_tree_string(ts)
    l1, l2 = tree_utils.calc_biparts(restree)
    if ("L1" in l1[0] and "L2" in l1[0]) or ("R1" in l1[0] and "R2" in l1[0]):
        smallest_int = 0
    elif ("L1" in l1[0] and "R1" in l1[0]) or ("L2" in l1[0] and "R2" in l1[0]):
        smallest_int = 1
    elif ("L1" in l1[0] and "R2" in l1[0]) or ("L2" in l1[0] and "R1" in l1[0]):
        smallest_int = 2
    if verbose:
        print("---")
        print((smallest_int, l1, l2))
    return True, smallest_int, 0


def process_paup_info(outfilepath, verbose):
    treelike = {0: 0, 1: 0, 2: 0}
    smallest_b = False
    smallest = None
    smallest_int = None
    second_smallest = None
    correct = None
    next_best = None
    # with open(raxml_info_file_path+".0", "r") as info_result:
    ouf = open(outfilepath, "r")
    resstr = ouf.readlines()
    for x in resstr:
        if "Tree" in x:
            continue
        spls = x.strip().split()
        counter = int(spls[0])-1
        treelike[counter] = -float(spls[1])
        if smallest is None:
            smallest = treelike[counter]
            smallest_int = counter
            correct = treelike[counter]
        elif treelike[counter] > smallest:
            second_smallest = smallest
            smallest = treelike[counter]
            smallest_int = counter
        if counter is not 0 and second_smallest is None:
            second_smallest = treelike[counter]
        if counter is not 0 and next_best is None:
            next_best = treelike[counter]
        elif counter is not 0 and treelike[counter] > next_best:
            next_best = treelike[counter]
    if smallest - second_smallest > LNLIKETHRESH:
        smallest_b = True
    if verbose:
        print("---")
        print(outfilepath)
        print(treelike)
        print((smallest_int, test_trees[smallest_int]))
        print((correct, next_best, correct-next_best))
    return smallest_b, smallest_int, correct-next_best


def user_feedback_time(k, leaves, root_bipart_label):
    mean_time_secs = (time.time() - starttime) / \
        float(k - calc_start_k)
    if mean_time_secs > 60:
        if mean_time_secs > SECONDS_PER_HOUR:  # more than one hour
            mean_time_units = "hours"
            mean_time_scalar = SECONDS_PER_HOUR
        else:  # between 1 and 60 minutes
            mean_time_units = "minutes"
            mean_time_scalar = SECONDS_PER_MINUTE
    else:  # less than 60 seconds
        mean_time_units = "seconds"
        mean_time_scalar = 1

    # adjust for the duplicate bipart at the root
    # (until we hit it, then stop adjusting)
    adj = -1 if root_bipart_label is None else 0
    est_remaining_time_secs = mean_time_secs * \
        (len(leaves) - k + adj)

    if est_remaining_time_secs > SECONDS_PER_MINUTE:
        if est_remaining_time_secs > SECONDS_PER_HOUR:
            est_remaining_time_units = "hours"
            est_remaining_time_scalar = SECONDS_PER_HOUR
        else:  # between 1 and 60 minutes
            est_remaining_time_units = "minutes"
            est_remaining_time_scalar = SECONDS_PER_MINUTE
    else:  # less than 60 seconds
        est_remaining_time_units = "seconds"
        est_remaining_time_scalar = 1

    time_string = " | average node time {0:.2f} {1:s}".format(
        mean_time_secs / mean_time_scalar, mean_time_units) + \
        " | est. remaining time {0:.2f} {1:s}".format(
            est_remaining_time_secs / est_remaining_time_scalar,
            est_remaining_time_units)
    return time_string


def set_leaf_sets(nd, root_bipart_label, bifurcating = True):
    leafsets = {}
    # two daughter subtrees
    if bifurcating:
        leafsets["R1"] = set([nd.children[0].label, ] if nd.istip else
                             [l.label for l in nd.children[0].leaves()])
        leafsets["R2"] = set([nd.children[1].label, ] if nd.istip else
                             [l.label for l in nd.children[1].leaves()])
    else:
        leafsets["R1"] = set(nd.lvsnms())
        leafsets["R2"] = set(nd.lvsnms())

    # sibling/parent subtrees
    is_other_side_of_root = False  # used when we hit the root a second time
    skip_tip_child_of_root = False  # used when a child of root is a tip
    tip_child_label = None
    testsib = False
    for sib in nd.parent.children:
        if sib != nd:
            testsib = True
            # if one of the subtrees is the root, skip over it
            if len(sib.leaves()) + len(nd.leaves()) == len(leaves):
                # if we already processed this bipart (on other side of
                # the root), don't do it again
                if (root_bipart_label is not None):
                    is_other_side_of_root = True
                    break
                # get the subtrees opposite the root
                if len(sib.children) == 2:
                    leafsets["L1"] = set([sib.children[0].label, ]
                                         if sib.children[0].istip else
                                         [l.label
                                         for l in sib.children[0].leaves()])
                    leafsets["L2"] = set([sib.children[1].label, ]
                                         if sib.children[1].istip else
                                         [l.label
                                         for l in sib.children[1].leaves()])
                elif len(sib.children) == 0:
                    skip_tip_child_of_root = True
                    tip_child_label = sib.label
                else:
                    leafsets["L1"] = set(sib.lvsnms())
                    leafsets["L2"] = set(sib.lvsnms())
                    print(("Node %s does not have exactly 2 children. \
                            It will be skipped." % sib.label ))
                    #continue
                # remember that we've already done the root,
                # so we can skip it when we hit the other side
                root_bipart_label = nd.label

            # otherwise not at root, all connected subtrees have children
            else:
                # sibling subtree
                leafsets["L1"] = set([l.label for l in sib.leaves()])

                # the rest of the tree
                leafsets["L2"] = rootlabelset - \
                    (leafsets["R1"].union(leafsets["R2"]).union(
                        leafsets["L1"]))  # set()
    return leafsets, testsib, root_bipart_label, is_other_side_of_root, \
        skip_tip_child_of_root, tip_child_label


def n_quartets(leafsets):
    x = 1
    for t in list(leafsets.values()):
        x *= len(t)
    return x


def empty_rep(j):
    rep = {}
    rep["queue"] = results_queue
    rep["lock"] = lock
    rep["using_partitions"] = using_partitions
    rep["node_id"] = nd.label
    rep["replicate_id"] = str(j)
    rep["n_completed"] = n_completed
    rep["raxml_path"] = raxml_path
    rep["seqs"] = {}
    rep["seqs_names"] = {}
    return rep


def get_replicates(n_completed, results_queue, leafsets, bifurcating = True):
    replicates = []
    N = n_quartets(leafsets)
    # need to make sure we don't repeat

    if args.verbose:
        print(('number of possible quartets: ' + str(N)))

    if (N * MAX_QUARTET_ENUMERATION_THRESHOLD) < nreps and bifurcating:
        if args.verbose:
            print('too few quartets for random generation, will generate all \
                   and do a random draw')

        # generate all the quartets
        possible_quartets = []
        for l1 in leafsets['L1']:
            for l2 in leafsets['L2']:
                for r1 in leafsets['R1']:
                    for r2 in leafsets['R2']:
                        possible_quartets.append((l1, l2, r1, r2))

        # look through them in random order for suitable ones
        nonoverlapping_count = 0
        while len(replicates) < nreps and len(possible_quartets) > 0:
            proposed_quartet = random.sample(possible_quartets, 1)[0]
            possible_quartets.remove(proposed_quartet)

            if check_overlap and not check_overlap_aln(proposed_quartet):
                nonoverlapping_count += 1
                if args.verbose:
                    print(('non-overlap count: ' + str(nonoverlapping_count)))
                continue

            # if we made it here then the proposed rep is acceptable
            rep = empty_rep(len(replicates))
            for i, subtree_name in enumerate(['L1', 'L2', 'R1', 'R2']):
                leaf_name = proposed_quartet[i]
                rep['seqs'][subtree_name] = aln[leaf_name]
                rep['seqs_names'][subtree_name] = leaf_name

            replicates.append(rep)

        if len(replicates) < 1:
            print(('WARNING: generated all possible quartets ' +
                  'and did not find a suitable one! If you have the -O ' +
                  'flag enabled, alignment may not have enough data at ' +
                  'this edge (i.e. low partial decisiveness).'))

        elif len(replicates) < nreps:
            print(('WARNING: only ' + str(len(replicates)) + ' suitable ' +
                  'replicates for this node.'))

    else:
        if args.verbose:
            print('generating random quartets')

        observed_quartets = set([])
        for j in range(nreps):
            if args.verbose:
                print(('looking for unique replicate ' + str(j)))

            rep = None
            duplicate_count = 0
            nonoverlapping_count = 0

            # loop until we find an acceptable replicate, or we hit the
            # maximum allowed proportion to attempt
            while len(observed_quartets) < N * max_random_sample_proportion:
                proposed_quartet = set()
                proposed_rep = empty_rep(j)

                # generate a random replicate
                if bifurcating:
                    for subtree_name, leaf_names in list(leafsets.items()):
                        r = random.sample(leaf_names, 1)[0]

                        # should really be doing this check when loading files
                        if r not in aln:
                            print(('\nFATAL ERROR: name ' + r + ' not in alignment'))
                            sys.exit(1)

                        if args.verbose:
                            print((" " + subtree_name + ' = ' + r))

                        proposed_rep['seqs'][subtree_name] = aln[r]
                        proposed_rep['seqs_names'][subtree_name] = r
                        proposed_quartet.add(r)
                else:
                    r1 = random.sample(leafsets["L1"],1)[0]
                    r2 = random.sample(leafsets["L2"],1)[0]
                    while r2 == r1:
                        r2 = random.sample(leafsets["L2"],1)[0]
                    r3 = random.sample(leafsets["R1"],1)[0]
                    r4 = random.sample(leafsets["R2"],1)[0]
                    while r4 == r3:
                        r4 = random.sample(leafsets["R2"],1)[0]
                    r = [r1,r2,r3,r4]
                    for k,nm in zip(r,["L1","L2","R1","R2"]):
                        if k not in aln:
                            print(('\nFATAL ERROR: name ' + r + ' not in alignment'))
                            sys.exit(1)
                        if args.verbose:
                            print((" " + nm + ' = ' + k))
                        proposed_rep['seqs'][nm] = aln[k]
                        proposed_rep['seqs_names'][nm] = k
                        proposed_quartet.add(k)

                if proposed_quartet in observed_quartets:
                    duplicate_count += 1
                    if args.verbose:
                        print(('duplicate count: ' + str(duplicate_count)))
                    continue

                # quartet is unique, remember that we tried it
                observed_quartets.add(frozenset(proposed_quartet))

                if check_overlap and not check_overlap_aln(proposed_quartet):
                    nonoverlapping_count += 1
                    if args.verbose:
                        print(('non-overlap count:' +
                              str(nonoverlapping_count)))
                    continue

                # if we made it here then the proposed rep is acceptable
                rep = proposed_rep
                if args.verbose:
                    print(("passed taxa", ",".join(list(proposed_quartet))))
                break

            if rep is None: # if there is no rep, then we hit the max number of attempts
                print((('WARNING: generated ~%0.0f%% of possible quartets ' +
                      'and did not find a suitable one! If you have the -O ' +
                      'flag enabled, alignment may not have enough data at ' +
                      'this edge (i.e. low partial decisiveness).') %
                      (max_random_sample_proportion * 100)))
                break

            elif args.verbose:
                print(('constructed replicate ' + str(j) + '\n'))

            replicates.append(rep)

    return replicates


def process_rep_results(results_queue, record_detail=False):
    detail_name_sets = []
    detail_tree_sets = []
    tree_counts_detailed = 0
    while not results_queue.empty():
        result = results_queue.get()
        smallest_b = None
        smallest_int = None
        diff = None
        # open the raxml info file
        if PAUP is False:
            raxml_info_file_path = "RAxML_info.temp_tree_search." + \
                result["label"]
            raxml_tree_file_path = "RAxML_result.temp_tree_search." + \
                result["label"]
            if os.path.exists(raxml_info_file_path+".0") is False and \
               os.path.exists(raxml_tree_file_path) is False:
                continue
            # smallest_b, smallest_int, diff = process_raxml_info(
            #    raxml_info_file_path, args.verbose)
            if LNLIKETHRESH > 0:
                smallest_b, smallest_int, diff = process_raxml_info_2lk(
                    result["raxml_stdout"], args.verbose)
            else:
                smallest_b, smallest_int, diff = process_raxml_info_ML(
                    raxml_tree_file_path, args.verbose)
        else:  # using paup
            unique_label = result["label"]
            resfl = "temp_inseqs." + unique_label + ".out"
            if os.path.exists(resfl) is False:
                continue
            smallest_b, smallest_int, diff = process_paup_info(
                resfl, args.verbose)
        if smallest_b is True:
            tree_counts[smallest_int] += 1
        tree_counts_detailed = tree_counts_detailed + diff
        # this will record the taxa included and the tree
        if record_detail:
            detail_name_sets.append(set(result["seqs_names"].values()))
            detail_tree_sets.append(smallest_int)
    return detail_name_sets, detail_tree_sets, tree_counts_detailed


def logn(freq, num):
    return math.log(freq, num)


def calc_ica_freq(counts, verbout = None):
    t1c = counts[0]
    t2c = counts[1]
    t3c = counts[2]
    total = float(sum([t1c, t2c, t3c]))
    if total == 0:
        return -1, 0
    freq1 = t1c/total
    freq2 = t2c/total
    freq3 = t3c/total
    tc = 3 - [t1c, t2c, t3c].count(0)
    ica = 1
    if tc > 1:
        if freq1 > 0.0:
            ica += freq1 * logn(freq1, tc)
        if freq2 > 0.0:
            ica += freq2 * logn(freq2, tc)
        if freq3 > 0.0:
            ica += freq3 * logn(freq3, tc)
    if t1c < max(t2c, t3c):
        ica *= -1
    if args.verbout:
        verbout.write(str(freq1) + "," + str(freq2) + "," + str(freq3) + "," + str(ica) + "\n")
    return ica, freq1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("-t", "--tree", type=open, nargs=1, required=True,
                        help="The input tree.")
    parser.add_argument("-n", "--alignment", type=open, nargs=1, required=True,
                        help="Alignment file in fasta format")
    parser.add_argument("-#", "--number-of-reps", type=int, nargs=1,
                        required=True, help="The number of replicate quartet \
                        topology searches to be performed at each node.")
    parser.add_argument("-T", "--number-of-threads", type=int, nargs=1,
                        required=True, help="The number of parallel threads to \
                        be used for quartet topology searches.")
    parser.add_argument("-q", "--partitions", type=os.path.abspath, nargs=1,
                        help="Partitions file in RAxML format. If omitted then \
                        the entire alignment will be treated as one partition \
                        for all quartet replicate topology searches.")
    parser.add_argument("-o", "--results-dir", type=os.path.abspath,
                        nargs=1, help="A directory to which output files will \
                        be saved. If not supplied, the current working \
                        directory will be used.")
    parser.add_argument("-r", "--result-prefix", type=str, nargs=1,
                        help="A prefix to put on the result files.")
    parser.add_argument("-e", "--temp-dir", type=os.path.abspath, nargs=1,
                        help="A directory to which temporary files will be \
                        saved. If not supplied, a \"temp\" directory will be \
                        created in the current working directory.")
    parser.add_argument("-s", "--start-node-number", type=int, nargs=1,
                        help="An integer denoting the node to which to start \
                        from. Nodes will be read from topologically identical \
                        (and isomorphic!) input trees in deterministic order, \
                        so this argument may be used to restart at an \
                        intermediate position (in case the previous run was \
                        canceled before completion, for example).")
    parser.add_argument("-p", "--stop-node-number", type=int, nargs=1,
                        help="An integer denoting the node at which to stop. \
                        Will include nodes with indices <= the stop \
                        node number. This argument may be used to limit the \
                        length of a given run in case only a certain part of \
                        the tree is of interest. Nodes will be read from \
                        topologically identical (and isomorphic!) input trees \
                        in deterministic order.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Provide \
                        more verbose output if specified.")
    parser.add_argument("-X", "--raxml-executable", nargs=1, help="The name \
                        (or absolute path) of the raxml executable to be used \
                        for calculating likelihoods on quartet topologies.")
    parser.add_argument("-L", "--lnlike-thresh", type=float, nargs=1, help="\
                         The lnlike threshhold that is the minimum a quartet\
                         must be to be considered better than others.")
    parser.add_argument("-O", "--min-overlap", type=int, help="The minimum \
                        sites required to be sampled for all taxa in a given \
                        quartet. ")
    parser.add_argument('-M', '--max-random-sample-proportion', type=float,
                        help='The proportion of possible replicates explored \
                        unsuccessfully by the random generation procedure \
                        before it gives up. Because this generates random \
                        replicates, it takes progressively longer as \
                        it proceeds. To avoid long runtimes, the recommended \
                        range is < ' +
                        str(DEFAULT_MAX_RANDOM_SAMPLE_PROPORTION) +
                        '(which is the default).')
    parser.add_argument("-C", "--clade", type=str, help="Conduct analysis on \
                        specific clade identified by CSV taxon list")
    parser.add_argument("-P", "--paup", action="store_true", help="Should use paup \
                        instead of raxml.")
    parser.add_argument("-m", "--multiclade", action="store_true",help="Analysis \
                        to determine what the outlying taxa are if they exist.")
    parser.add_argument("-V", "--verbout", action="store_true", help="Provide \
                        output of the frequencies of each topology and ica")

    args = parser.parse_args()

    if args.max_random_sample_proportion:
        max_random_sample_proportion = args.max_random_sample_proportion
        print(('setting the maximum proportion of possible quartets to be explored \
              to: ' + str(max_random_sample_proportion)))
        if (max_random_sample_proportion >
           DEFAULT_MAX_RANDOM_SAMPLE_PROPORTION):
            print(('WARNING: for some alignments, the quartet randomization \
                   procedure may take a long time to finish (or fail) when \
                   max proportion of quartets to sample is greater than \
                   ' + str(DEFAULT_MAX_RANDOM_SAMPLE_PROPORTION)))

    if args.paup:
        PAUP = True

    if args.lnlike_thresh:
        LNLIKETHRESH = args.lnlike_thresh[0]
        print(("setting the minimum lnlike thresh to be " + str(LNLIKETHRESH)))

    results_dir = os.path.abspath(args.results_dir[0]) \
        if args.results_dir is not None else os.path.abspath(".")
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)

    result_prefix = "RESULT"
    if args.result_prefix is not None:
        result_prefix = args.result_prefix[0]

    tree_result_file_path = results_dir + "/"+result_prefix+".labeled.tre"
    score_result_file_path = results_dir + "/"+result_prefix+".node_scores.csv"
    verbout = None
    if args.verbout:
        verbout = open(results_dir + "/" + result_prefix + ".verbout", "w")
        verbout.write("topo1,topo2,topo3,ica\n")

    if args.temp_dir is not None:
        temp_wd = args.temp_dir[0]
        print(("setting the temp working dir to " + temp_wd))
    if not os.path.exists(temp_wd):
        print(("creating " + temp_wd))
        os.mkdir(temp_wd)

    calc_start_k = args.start_node_number[0] if args.start_node_number is not \
        None else 1

    using_partitions = False
    if args.partitions is not None:
        using_partitions = True
        parts_file_path = os.path.abspath(args.partitions[0])

    raxml_path = args.raxml_executable[0] if args.raxml_executable is not \
        None else DEFAULT_RAXML
    nprocs = args.number_of_threads[0]
    nreps = args.number_of_reps[0]

    #  shared object access for multithreading
    manager = Manager()
    lock = manager.Lock()

    #  read the alignment into a dict, assumes fasta
    #  unbroken on lines
    aln = {}
    alnfile = args.alignment[0]
    print(("reading alignment from " + alnfile.name))
    firstline = True
    aln_length = 0
    for i in seq.read_fasta_file_iter(alnfile.name):
        aln[i.name] = i.seq
        aln_length += len(i.seq)
    # for getting the overlap between test seqs
    record_overlap_for_tips(aln)

    if args.min_overlap:
        check_overlap = True
        if aln_length < args.min_overlap:
            print(('WARNING: the alignment length is less than the minimum \
                   overlap. The minimum overlap required will be \
                   ' + str(DEFAULT_MIN_OVERLAP)))
        else:
            min_overlap = args.min_overlap
            print(("setting the minimum overlap to be " + str(min_overlap)))

    # get the tree to subsample
    tree = None
    treefile = args.tree[0]
    print(("reading tree from " + treefile.name))
    tree = tree_reader.read_tree_string(treefile.readline())
    if tree is None:
        sys.exit("Could not find a tree in the treefile: " + treefile.name)
    args.tree[0].close()
    leaves = tree.leaves()
    rootlabelset = set()
    for l in leaves:
        rootlabelset.add(l.label)

    calc_stop_k = args.stop_node_number[0] if args.stop_node_number is not \
        None else len(tree.leaves())+100
    if calc_stop_k < calc_start_k:
        sys.exit("The start node number is higher than the stop node number, \
                 designating no nodes for processing.")

    just_clade = False
    clade = None
    clade_names = None
    if args.clade is not None:
        names = args.clade.split(",")
        nodes = []
        just_clade = True
        print("Just calculating for clade ", names)
        for i in names:
            found = False
            for j in tree.leaves():
                if j.label == i:
                    nodes.append(j)
                    found = True
                    break
            if found is False:
                print((i, "not found. Exiting."))
                sys.exit()
        clade = tree_utils.get_mrca(nodes, tree)
        clade_names = clade.lvsnms()
        #make the ingroup multifurcating
        if args.multiclade:
            while len(clade.children) > 0:
                for i in clade.children:
                    clade.remove_child(i)
            for i in clade_names:
                nnd = Node()
                nnd.parent = clade
                nnd.istip = True
                nnd.label = i
                clade.add_child(nnd)
        print(clade.get_newick_repr(False))

    if args.verbose:
        print(("tree has " + str(len(leaves)) + " leaves"))

    # k is the node counter
    k = 1

    #  if we are starting at the beginning, initialize the results file
    #  (otherwise assume it's already there and don't overwrite it)
    if not calc_start_k > k:
        with open(score_result_file_path, "w") as resultsfile:
            resultsfile.write("node_label,obs_freq_of_test_bipart,ica,qs_freq,qs_score,diff,num_replicates,notes\n")

    # process the nodes in the tree
    starttime = time.time()
    root_bipart_label = None
    numnodes = str(len(list(tree.iternodes()))-len(list(tree.leaves())))
    tc = 0
    for nd in tree.iternodes():
        if clade is not None:
            if nd is not clade:
                continue
        tc += 1
        os.chdir(temp_wd)
        subprocess.call("rm *", shell=True)

        if k > calc_stop_k:
            print("Processed all nodes up to the stop node. Quitting now")
            exit()

        write_test_trees(".")
        # skip tips and root
        if nd.istip or nd.parent is None:
            """
            if nd.istip:
                try:
                    int(nd.label)
                    new_label = "T"+nd.label
                    print("renaming tip node with numeric label '" +
                          nd.label + "' to " + new_label + " to avoid \
                          duplicating numeric internal node labels.")
                    nd.label = new_label
                except ValueError:
                    continue
            if (args.verbose):
                print("\nskipping " + ("tip " +
                      nd.label if nd.label is not None else "root"))
            """
            continue

        #  record the node label in the tree, these are required for user to
        #  match scores with corresponding branches
        nd.label = str(k)

        if (k < calc_start_k):
            #  skip nodes if we have a specified start node (i.e. not the root)
            #  and we haven't hit it yet
            k += 1
            continue
        else:
            # provide user feedback before incrementing
            if k > calc_start_k:
                time_string = user_feedback_time(k, leaves, root_bipart_label)
            else:
                time_string = ""
            print(("\nprocessing node " + str(k) + "/" + numnodes + time_string))

        #  require a bifurcating tree
        #  assert(len(node.children) == 2)
        bifurc = True
        if len(nd.children) != 2:
            print(("Node %s does not have exactly 2 children. \
                  It will be skipped." % k))
            bifurc = False
            #continue
        
        # get leaf sets for the four connected subtrees
        leafsets, testsib, root_bipart_label, is_other_side_of_root, \
            skip_tip_child_of_root, tip_child_label \
            = set_leaf_sets(nd, root_bipart_label,bifurc)

        # there is some case that the sib has no other
        if testsib is False:
            print("other sib not found")
            continue
        # no more user feedback, now we can increment k
        k += 1

        if skip_tip_child_of_root:
            print(("not calculating ica for tip child '" + tip_child_label +
                  "' of the root (ica is 1.0, as for all tips)."))
            continue

        # if we already processed bipart at root and this is other side of that
        if is_other_side_of_root:
            print(("\nskipping second instance of root-adjacent bipartition" +
                  "(it was already processed at node " +
                  root_bipart_label + ")."))
            nd.label = root_bipart_label
            continue

        # sanity check
        t = set()
        for leafset in list(leafsets.values()):
            assert len(leafset) > 0
            t.update(leafset)
        assert len(t) == len(leaves)
        del(t)

        results_queue = manager.Queue()
        n_completed = manager.Value("i", 0, "lock")
        replicates = get_replicates(n_completed, results_queue, leafsets, bifurc)
        notes = ''
        if len(replicates) < 1:
            ica = 'NA'
            freq = 'NA'
            diff = 'NA'
            qs_freq = 0
            qs_score = 0
            notes = 'found no suitable replicates'
            nd.data["replicates"] = "%s" % float("%.2g" % 0)
            nd.data["qs_freq"] = "%s" % float("%.2g" % 0)
            nd.data["qs_score"] = "%s" % float("%.2g" % 0)
            nd.data["ica"] = ""
            nd.data["freq"] = ""

        else:  # there were at least some suitable replicates

            # clear lingering files from previous runs that interfere w/ raxml
            # redirecting stderr as it prints failed calls not sure why as the
            # command seems to be working as expected...
            subprocess.call("rm *." + nd.label + ".* 2> /dev/null", shell=True)

            # copy original partitions file, should not change throughout run
            if using_partitions:
                subprocess.call("cp "+parts_file_path+" temp_parts", shell=True)

            # run the raxml calls in parallel
            # now designate multiprocessing resource pool.
            # important to do outside node loop. garbage collecting does not
            # apply to threads! set maxtasksperchild to release mem and files

            pool = Pool(processes=nprocs, maxtasksperchild=1)  # only py 2.7
            if PAUP:
                pool.map(process_replicate_paup, replicates)
            else:
                pool.map(process_replicate, replicates)
            pool.close()
            pool.join()
            del(pool)

            print("")

            # now process the results. first open a file to hold topologies
            # sending just_clade = True will give back detailed name results
            detail_name_results, detail_tree_results, diff = \
                process_rep_results(results_queue, just_clade)

            if just_clade:
                nm_dict = {}
                for j in detail_name_results:
                    for k in j:
                        if k not in nm_dict:
                            nm_dict[k] = {0: 0, 1: 0, 2: 0}
                count = 0
                for j in detail_name_results:
                    for k in j:
                        nm_dict[k][detail_tree_results[count]] += 1
                    count += 1
                with open(score_result_file_path+".clade", "w") as clade_file:
                    nhead = ["taxon", "tree1", "tree23", "ica", "freq1"]
                    clade_file.write(",".join(nhead) + "\n")
                    for j in nm_dict:
                        if j not in clade_names:
                            continue
                        nica, nfreq = calc_ica_freq(nm_dict[j])
                        vals = str(nm_dict[j][0]) + "," + str(nm_dict[j][1] +
                                                              nm_dict[j][2]) + \
                            "," + str(nica) + "," + str(nfreq) + "\n"
                        clade_file.write(j+","+vals)

            ica, freq = calc_ica_freq(tree_counts, verbout)
            nd.data["freq"] = "%s" % float("%.2g" % freq)
            nd.data["ica"] = "%s" % float("%.2g" % ica)
            qs_freq = freq
            qs_score = ica
            nd.data["qs_freq"] = "%s" % float("%.2g" % freq)
            nd.data["qs_score"] = "%s" % float("%.2g" % ica)
            nd.data["replicates"] = "%s" % float("%.2g" % len(replicates))
            tree_counts = {0: 0, 1: 0, 2: 0}

        # write the scores to the file
        with open(score_result_file_path, "a") as results_file:
            results_file.write(",".join([nd.label, str(freq), str(ica),
                               str(qs_freq), str(qs_score), str(diff),
                               str(len(replicates)), notes]) + "\n")

        # clean up
        del(results_queue)
        del(n_completed)
        #break

    write_figtree(tree_result_file_path+".figtree", tree)

    ### LEAVING THESE FOR SIMS, BUT REMOVE AFTER THAT AND JUST USE THE
    ### MULTILABELED ONE, FREQ IS GOING TO BE QS_FREQ UNTIL AFTER SIMS
    # write the tree with all processed nodes labeled
    with open(tree_result_file_path, "w") as tree_file_path:
        tree_file_path.write(tree.get_newick_repr(True)+";")

    # write a tree with the frequencies at the nodes
    for i in tree.iternodes():
        if len(i.children) > 1 and i is not tree and "freq" in i.data:
            i.label = i.data["qs_freq"]
        elif len(i.children) > 1:
            i.label = ""
    # with open(tree_result_file_path.rsplit('.tre',1)[0]+".freq.tre", "w") as tree_file_path:
    with open(tree_result_file_path+".freq", "w") as tree_file_path:
        tree_file_path.write(tree.get_newick_repr(True)+";")

    # write a tree with the ica scores at the nodes
    for i in tree.iternodes():
        if len(i.children) > 1 and i is not tree and "ica" in i.data:
            i.label = i.data["ica"]
        elif len(i.children) > 1:
            i.label = ""
    # with open(tree_result_file_path.rsplit('.tre',1)[0]+".ica.tre", "w") as tree_file_path:
    with open(tree_result_file_path+".ica", "w") as tree_file_path:
        tree_file_path.write(tree.get_newick_repr(True)+";")

    print(("\ndone.\nscores written to: " + score_result_file_path +
          "\nlabeled tree written to: " + tree_result_file_path +
          "\ntotal time {0:.2f}".format((time.time() - starttime) / 60 / 60) +
          " hours"))

    if args.verbout:
        verbout.close()
