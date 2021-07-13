# Remove repeated email sub-threads

## Overview
A python script to detect and remove duplicated email messages within a folder of files. This detects complete duplicates as well as sub-threads; emails whose contents are present in one or more other email file in the folder. Repeated messages are deleted from the folder. If the repeated message has any attachments, they are extracted and saved before deletion. Currently this is only functional for eml files.

## Usage
Specify the path to the folder containing emails to be checked using the `--dir` parameter. An error message will print if the specified directory does not exist.

Syntax is as follows:
`python3 remove_subthreads.py --dir=Documents/emails`
