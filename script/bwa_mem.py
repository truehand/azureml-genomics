# ---------------------------------------------------------
"""This module will run bwa"""

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

    parser.add_argument("--ref_genome_index", type=str, default="")
    parser.add_argument("--output_folder", type=str, default="")
    parser.add_argument("--cpu_threads", type=int, default=2)
    args, _ = parser.parse_known_args()

    global ref_genome_index
    global output_folder
    global cpu_threads
    ref_genome_index = args.ref_genome_index
    output_folder = args.output_folder
    cpu_threads = args.cpu_threads
    print("ref_genome_index:", ref_genome_index)
    print ("output folder:", output_folder)
    print ("cpu_threads:", cpu_threads)


def run(mini_batch):
    # check each file's size and print
    processed_files = []
    for r1 in mini_batch:
        r2 = r1
        print("output folder:", output_folder)
        print("Processing file: ", r1)
        if r1.endswith('_R2.fastq.gz'):
            # ignore R2 files
            continue
        elif r1.endswith('_R1.fastq.gz'):
            r2 = r1.replace('_R1.fastq.gz', '_R2.fastq.gz')
            if not os.path.isfile(r2):
                print("Error: R1 and R2 files are not paired")
                raise Exception("Error: R1 and R2 files are not paired")
        sam_file = os.path.basename(r1)
        sam_file = sam_file.replace('_R1.fastq.gz', '.sam')
        cmd = 'cp  ' + ref_genome_index + '/* ./ && bwa mem hg38 -t ' + cpu_threads + ' ' + r1 + ' ' + r2 + ' -o ' + output_folder + "/" + sam_file
        try:
            print("Running command: ", cmd)
            p = Popen(cmd, shell='True', stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            print("stdout: ", stdout)
            print("stderr: ", stderr)
            processed_files.append(sam_file)
        except Exception as e:
            print("Error in user command: ", e)
            raise e
    return processed_files