#!/usr/bin/python

"""This python file includes the incremental clustering algorithm applied in BAESE"""

import editdistance
from source import Cluster, LogLine
import cluster_config


def clustering(log_line_list, st):
    # choose k-mer length for filter
    if st > 0.9:
        kmer_size = 10
    elif 8 / 9 < st <= 0.9:
        kmer_size = 9
    elif 0.875 < st <= 8 / 9:
        kmer_size = 8
    elif 6 / 7 < st <= 0.875:
        kmer_size = 7
    elif 5 / 6 < st <= 6 / 7:
        kmer_size = 6
    elif 0.8 < st <= 5 / 6:
        kmer_size = 5
    elif 0.75 < st <= 0.8:
        kmer_size = 4
    elif 2 / 3 < st <= 0.75:
        kmer_size = 3
    else:
        kmer_size = 2

    # instanciate the kmer dictionary
    kmer_dictionary = {}

    # dictionary of clusters
    cluster_dictionary = {}
    cluster_id = 0
    count = 0

    for line in log_line_list:
        count += 1
        cluster_candidates = []
        tmp_cluster_candidate = None

        # check if log line is already representative of cluster
        if line.line_text in cluster_dictionary:
            cluster_dictionary[line.line_text].log_line_list.append(line)
            continue

        # intelligent length filter using a short word filer + calculating Levenshtein metric
        # calculate kmer dictionary of log line
        kmer_dictionary.clear()

        for i in range(0, len(line.line_text) - kmer_size):
            kmer = line.line_text[i:i + kmer_size]
            if kmer in kmer_dictionary:
                kmer_dictionary[kmer] += 1
            else:
                kmer_dictionary[kmer] = 1

        # find cluster candidates and calculate LS metric
        for key in cluster_dictionary:
            # check if length of line is in [key-ST*key, key + ST*key]
            if not st * len(key) <= len(line.line_text) <= (2 - st) * len(key):
                continue

            # Short word filter
            # L - K + 1 - (1 - p) * K * L | L: window length (longer sequence), K: kmer_size, p: threshold
            swt = max(len(line.line_text), len(key)) - kmer_size + 1 - (
                        (1 - st) * kmer_size * max(len(line.line_text), len(key)))

            kmer_equal = 0

            for kmer in kmer_dictionary:
                if kmer in cluster_dictionary[key].kmer_dic:
                    kmer_equal += min(kmer_dictionary[kmer], cluster_dictionary[key].kmer_dic[kmer])

            if kmer_equal >= swt:
                # calculate LS metric
                lss = 1 - editdistance.eval(line.line_text, key) / max(len(line.line_text), len(key))

                if lss >= st:
                    if tmp_cluster_candidate is None:
                        tmp_cluster_candidate = [key, lss, kmer_equal]
                        cluster_candidates = [[key, lss, kmer_equal]]
                    else:
                        if lss > tmp_cluster_candidate[1]:
                            tmp_cluster_candidate = [key, lss, kmer_equal]
                            cluster_candidates = [[key, lss, kmer_equal]]
                        elif lss == tmp_cluster_candidate[1] and kmer_equal > tmp_cluster_candidate[2]:
                            tmp_cluster_candidate = [key, lss, kmer_equal]
                            cluster_candidates = [[key, lss, kmer_equal]]
                        elif lss == tmp_cluster_candidate[1] and kmer_equal == tmp_cluster_candidate[2] and len(
                                key) > len(tmp_cluster_candidate[0]):
                            tmp_cluster_candidate = [key, lss, kmer_equal]
                            cluster_candidates = [[key, lss, kmer_equal]]
                        elif lss == tmp_cluster_candidate[1] and kmer_equal == tmp_cluster_candidate[2] and len(
                                key) == len(tmp_cluster_candidate[0]):
                            cluster_candidates.append([key, lss, kmer_equal])

        # add new cluster to dictionary or add line to other cluster
        if len(cluster_candidates) == 1:
            cluster_dictionary[tmp_cluster_candidate[0]].log_line_list.append(line)
            line.cluster = tmp_cluster_candidate[0]
        elif len(cluster_candidates) > 1:
            tmp_cluster_candidate = cluster_candidates[0]
            cluster_dictionary[tmp_cluster_candidate[0]].log_line_list.append(line)
            line.cluster = tmp_cluster_candidate[0]
        # if cluster_candidates is empty, generate a new cluster
        elif not bool(cluster_candidates):
            cluster_dictionary[line.line_text] = Cluster.Cluster(cluster_id, line.line_text, kmer_dictionary)
            cluster_dictionary[line.line_text].log_line_list.append(line)
            cluster_id += 1
            line.cluster = line.line_text

        if count % 1000 == 0:
            print('{0} lines have been clustered! {1} clusters found so far...'.format(count, len(cluster_dictionary)))

    return cluster_dictionary


# The incremental clustering only works for ST higher than/equal to 0.5
if cluster_config.st < 0.5:
    st = 0.5
    print(
        'The similarity threshold has been set to 0.5, because the incremental clustering requires an threshold higher than or equal to 0.5.')

# import log data and preprocess
line_id = 0
log_line_list = []

print('Import {0}!'.format(cluster_config.input_file))

with open(cluster_config.input_file) as f:
    for line in f:
        if (line_id + 1) % 100000 == 0:
            print('{0} lines have been imported!'.format(line_id + 1))
        # Remove characters that should not occur in log data. According to RFC3164 only ascii code symbols 32-126
        # should occur in log data.
        line = ''.join([x for x in line if 31 < ord(x) < 127])
        line = line.strip(' \t\n\r')
        if cluster_config.timestamp_length == -1 or cluster_config.timestamp_length is None:
            log_line = LogLine.LogLine(line_id, line, line)
        else:
            log_line = LogLine.LogLine(line_id, line, line[(cluster_config.timestamp_length + 1):])
        line_id += 1
        log_line_list.append(log_line)
f.close()

print('Finished import of "{0}"!'.format(cluster_config.input_file))
print('{0} lines have been imported!'.format(line_id))

# Cluster the log data
cluster_dictionary = clustering(log_line_list, cluster_config.st)
print('{0} clusters found!'.format(len(cluster_dictionary)))

# Sort clusters by size in ascending order
sorted_cluster_dictionary_keys = [elem for _, elem in sorted(
    zip([len(x.log_line_list) for x in cluster_dictionary.values()], list(cluster_dictionary.keys())))]

# Write output
with open(cluster_config.output_file, "w") as output:
    for cluster in sorted_cluster_dictionary_keys:
        text = "cluster representative: " + cluster_dictionary[cluster].cluster_representative + "\nsize: " + str(
            len(cluster_dictionary[cluster].log_line_list)) + "\n"
        output.write(text)
        if cluster_config.write_members is True:
            for line in cluster_dictionary[cluster].log_line_list:
                text = "  " + line.line + "\n"
                output.write(text)
        output.write("\n")

print('Clusters written to {0}.'.format(cluster_config.output_file))
