# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This module will run fastqc."""

import argparse
import os
from subprocess import Popen, PIPE
from pathlib import Path

def init():
    print("Environment variables start ****")
    for key, val in os.environ.items():
        print(key, val)
    print("Environment variables end ****")

    parser = argparse.ArgumentParser(
        allow_abbrev=False, description="ParallelRunStep Agent"
    )

    parser.add_argument("--output_folder", type=str, default=0)
    args, _ = parser.parse_known_args()

    global output_folder
    output_folder = args.output_folder
    print ("output folder:", output_folder)

def run(input_folder):
    # check each file's size and print
    processed_files = []
    for file_name in input_folder:
        print("output folder:", output_folder)
        print("Processing file: ", file_name)
        cmd = 'du -h ' + file_name
        try:
            print("Running command: ", cmd)
            p = Popen(cmd, shell='True', stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            print("stdout: ", stdout)
        except Exception as e:
            print("Error in user command: ", e)
            raise e

        # run sequana_fastqc for entire folder
        cmd = 'fastqc ' + file_name + ' -o ' + output_folder
        try:
            print("Running command: ", cmd)
            p = Popen(cmd, shell='True', stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            print("stdout: ", stdout)
        except Exception as e:
            print("Error in user command: ", e)
            raise e
        processed_files.append(file_name)
    return processed_files
