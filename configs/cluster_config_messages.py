st = 0.6 # Similarity threshold for clustering [0, 1]
input_file = 'data/in/messages' # Path to input log file
output_file = 'data/out/clusters.txt' # Path to output file
timestamp_length = 15 # Length of time stamp at beginning of log line that will be removed; set to -1 for no timestamp
write_members = True # Set whether output file will only contain cluster representatives or all cluster members [True, False]
