FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04

ENV AZUREML_CONDA_ENVIRONMENT_PATH /azureml-envs/tensorflow-2.7
# Create conda environment
RUN conda create -p $AZUREML_CONDA_ENVIRONMENT_PATH \
    python=3.8 pip=20.2.4

# Prepend path to AzureML conda environment
ENV PATH $AZUREML_CONDA_ENVIRONMENT_PATH/bin:$PATH

# Install pip dependencies
RUN pip install --use-feature=2020-resolver \
                                          'azureml-core' \
                                          'azureml-defaults' \
                                          'azureml-mlflow' \
                                          'azureml-telemetry' \
                                          'debugpy'
                          
# This is needed for mpi to locate libpython
ENV LD_LIBRARY_PATH $AZUREML_CONDA_ENVIRONMENT_PATH/lib:$LD_LIBRARY_PATH
RUN echo "nameserver 8.8.8.8" | tee /etc/resolv.conf > /dev/null
RUN apt-get install -y apt-transport-https ca-certificates libffi7
RUN apt-get update

RUN apt-get install -y bwa samtools

# Use precompiled binaries (recommended)
#RUN curl -L https://github.com/bwa-mem2/bwa-mem2/releases/download/v2.0pre2/bwa-mem2-2.0pre2_x64-linux.tar.bz2 \
#  | tar jxf -

#RUN ln -s bwa-mem2-2.0pre2_x64-linux/bwa-mem2 /usr/bin/bwa-mem2
# usage:
# bwa-mem2 index ref.fa
# bwa-mem2 mem ref.fa read1.fq read2.fq > out.sam