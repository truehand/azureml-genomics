# Azure ML for Genomics Pipelines

This is an Azure Machine Learning (Azure ML) pipeline example that demonstrates how we can run genomics workflows using Azure ML v2. The example is quite simple, it only performs sequence quality check (using _fastqc_) on input sequence data and generates SAM files from the same set of paired DNA sequences (using the _bwa_ tool). The pipeline is designed to be scalable and can be run on a large number of input files in parallel. The pipeline is also designed to be highly available and fault tolerant, and can be run on a cluster of Azure ML compute nodes.

Please read this blog entry for some more background on this approach on the [Microsoft Tech Community](https://techcommunity.microsoft.com/t5/ai-machine-learning-blog/introducing-scalable-and-enterprise-grade-genomics-workflows-in/ba-p/3752222)

The pipeline consists of three jobs, two of which run in parallel. The first job, seq_quality_control, performs quality control on input sequence data using the FastQC tool. The second job, bwa_index, creates an index for the reference genome used in the alignment step. Once the index is created, the third job, bwa, kicks off and aligns the input sequence data to the reference genome using the Burrows-Wheeler Aligner (BWA) tool. This BWA step processes paired input ".fa.gz" reads in parallel across multiple nodes of an Azure ML cluster with auto-scale.

## Pipeline Architecture
![genomics workflow](./images/genomics_workflow.png)

The pipeline is defined as a YAML file, pipeline.yml, which can be executed in an Azure ML workspace. The pipeline runs on an elastic Azure ML compute cluster that is called "genomics-cluster" in this example, and the input and output data are stored in an Azure Blob Storage datastore associated with the same instance of an Azure ML workspace.

The pipeline is designed to handle large data sets and is optimized for parallel processing. The seq_quality_control and bwa jobs are run in parallel on multiple instances, each with a specified number of CPU threads (specified with bwa's -t parameter). The pipeline also includes retry settings in case of job failures and central logging to help diagnose issues.

Step 1 and 2 can start simultaneously as there are no interdependencies between them. Step 2 and 3 can process input files in parallel. Each step requires a different software environment, and these environments are also defined and registered in our Azure ML workspace. 


## Pipeline Steps

- seq_quality_control

This job performs quality control on the input sequence data using the FastQC tool. The job runs in parallel on multiple nodes. The output of the job is stored in an Azure Blob Storage datastore. It leverages a fastqc environment registered in our workspace. This environment can be created using the environment.yml and Dockerfile contained within env-fastq folder.

This step uses the "parallel" mode, which requires a run script called "fastqc_parallel.py". Overall, this script is designed to run the fastqc tool on each input file in parallel, and generate the output report in the specified output folder.

- bwa_index

This job creates an index for the reference genome used in the alignment step. The job is run on a single instance as it cannot be run in parallel, and uses the BWA Indexer component registered by Azure ML. [Pipeline components](https://learn.microsoft.com/en-us/azure/machine-learning/concept-component) defined by users can be centrally registered so that they can be re-used in other pipelines. They are versioned and there is an audit log for which pipeline jobs have utilised them. Only this step is a centrally registered,versioned and sharable step, to show how we can use a mix-and-match strategy to include different types of pipeline steps/jobs. The output of the job is stored in an Azure Blob Storage datastore, which can be accessed by any subsequent pipeline step.

- bwa

This job aligns the input sequence data to the reference genome using the BWA tool. The job runs in parallel on four instances, each with a single CPU thread. The output of the job is stored in an Azure Blob Storage datastore.

Both the bwa and seq_quality_control steps are of type run_function. To read more on this type of jobs please visit:

https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-job-in-pipeline?tabs=cliv2

This type of jobs requires a Python script that has two functions: _init()_ and _run()_:

- _init()_ is used for common preparation before starting mini-batches, for example, use it to load and initialise any packages/models etc that you may use under the run() function
- _run(mini_batch)_ will be run once for every single file under a directory specified by its input parameter _mini_batch_. These runs are automatically distributed across the cluster nodes.

## Creating components and environments

To register the bwa_index component into an ML workspace called my-azureml-workspace, registered as version #3:

`az ml component create --file bwa_index.yml --workspace-name my-azureml-workspace --resource-group demo --version 3`

Similarly, an environment can be defined as follows:

`az ml environment create --file ./env-bwa/environment.yml --resource-group demo --workspace-name my-azureml-workspace --name bwa --version 5`

Of course, these commands require the az cli to be authenticated beforehand, for which one can run:

`az login`

## Pipeline Inputs and Outputs

The pipeline takes input sequence data from an Azure Blob Storage datastore and outputs the quality control results and alignment output to another Azure Blob Storage datastore. The pipeline also creates a log file for each job, which is stored in the same Azure Blob Storage datastore as the job output.

You will need to provide the necessary input data and configure the pipeline YAML file accordingly. [Read more here](https://learn.microsoft.com/en-us/azure/machine-learning/concept-data) about how you can create individual files or folders as registered datasets.

In this example, the human reference genome, hg38, is defined in AzureML as a versioned, centrally registered dataset in our ML workspace, which in turn point to a publicly available file. Also as input, I have a few input fastq files in my Azure ML workspaces’ default datastore. 

![human reference genome](./images/human_ref_dataset.png)

Once registered, the above dataset can now be referred as "azureml:hg38:1" in pipeline.yml. The last number in this representation is the version of the file that has been registered within our workspace.

For the input DNA files, we create a folder in our Azure datastore and upload our input sequences, via Storage Explorer or some other mechanism preferred:

![upload paired seqeunces](./images/upload_genomic_data.png)

Then, we simply define a uri_folder for this location, which in turn, we can refer from our pipeline:

![paired input DNA](./images/input_dna.png)

 Unlike the above human reference genome, this time, this data URI is not a pointer to an external public location, but to an Azure ML datastore path in our Azure subscription.

## Azure ML compute

I [created](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=python) a CPU-based cluster within my workspace that has this type of VMs:

- Standard_D13_v2 (8 cores, 56 GB RAM, 400 GB disk)

![AML compute cluster](./images/genomics_cluster.png)

To minimise costs, I set it up as a low_priority cluster (spot instances), and set the minimum number of node as zero, and the maximum as 8.

This cluster is referred as "azureml:genomics-cluster" within the pipeline definition. Each step in the pipeline can use a different cluster, but in this example we use this "genomics-cluster" as the default compute across all steps.

## Running the Pipeline

Once you have set up your environment and configured the pipeline YAML file, you can submit the pipeline to Azure ML for execution. The pipeline will automatically provision the necessary resources and execute the jobs in the specified order.

Assuming your workspace is called "my-azureml-workspace", and your resource-group "demo", the job can be submitted from the command line as follows:

`az ml job create --file pipeline.yml --workspace-name my-azureml-workspace --resource-group demo --web`

## Next steps

It will be fantastic if you want to contribute to this repository by creating other re-usable components and environments that can be used from within other pipelines. Get in touch! 
