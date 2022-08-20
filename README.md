# aecid-incremental-clustering
An efficient method for clustering log data.


Please install the library editdistance before continuing. The aecid-incremental-clustering was tested with editdistance 0.3.1, but should work with other versions as well.
```
pip3 install editdistance
```

To get started, just clone this repository and execute
```
python3 incremental_clustering.py
```
to run the aecid-incremental-clustering with the default input file and configurations. To change the configuration, edit the cluster_config.py file.

There are two sample configurations for Exim Mainlog and Messages log. Just copy either of the configurations by
```
cp configs/cluster_config_mainlog.py ./cluster_config.py
```
or
```
cp configs/cluster_config_messages.py ./cluster_config.py
```
and then execute the main script as before.

The script generates a text file containing a list of clusters. To view the output, use
```
cat data/out/clusters.txt
```

More information on the aecid-incremental-clustering is provided in the following paper:

Incremental Clustering for Semi-Supervised Anomaly Detection applied on Log Data
