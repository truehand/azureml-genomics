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
# create man folder for jre
RUN mkdir -p /usr/share/man/man1
RUN apt-get install -y default-jre
RUN apt-get install -y fastqc