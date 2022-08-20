#!/usr/bin/python

"""This class describes log lines"""

import copy


class Cluster:
    def __init__(self, cluster_id, cluster_representative, kmer_dic={}):
        self.id = cluster_id
        self.log_line_list = []
        self.cluster_representative = cluster_representative
        self.kmer_dic = copy.deepcopy(kmer_dic)
