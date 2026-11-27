---
title: "Running ANTS on Condor"
date: 2013-03-19
kind: "tutorial"
summary: "A walkthrough of creating a study-specific MRI template with ANTS on a Condor cluster, using bash scripts that build a DAG file."
legacy:
  - "/running-ants-on-condor.html"
---

If you have ever used [ANTS](http://www.picsl.upenn.edu/ANTS/) you know it is amazing for image registration. Unfortunately, it can take hours or even days to complete. That is where [Condor](http://research.cs.wisc.edu/htcondor/) comes in. Here is how I created a study specific template with ANTS and Condor.

This walkthrough assumes that you know or are familiar with \*unix, ANTS and Condor. High-throughput Condor is a specialized workload management system for compute-intensive jobs, and I will assume that you already have it running on your favorite computing cluster. Using the scripts below, you should be able to create a study-specific MRI template using ANTS on your Condor system.

Ok, here we go. To summarize, I wrote a bash script that created a DAG file, which describes how to submit jobs to condor, which, in turn, execute bash scripts that run ANTS.

## Here are the files you will need.

- A set of programs to run and files to run them on. In my case this will be the ANTS executables, bash scripts to link executables together, and [nifti-format](http://nifti.nimh.nih.gov/nifti-1) T1 images.
- To run it in Condor, you will need a submit file for each command you want to run.
- Condor jobs can then be linked using a directed-acyclic graph, or DAG, file. Because DAG files can be complicated and study specific, I write scripts that create these files.

Once you have these parts, you will be able to run a script, and submit the DAG it creates to your condor system.

```bash
createAntsDag_nifti.sh template.nii templateMask.nii subject*.nii > myDag.dag
condor_submit_dag myDag.dag
```

## Programs and Files

First, set up a directory with executables in it. The executables you will need are all part of the [ANTS package](http://www.picsl.upenn.edu/ANTS/). For this code to work, you will need `ANTS, ImageMath, N3BiasFieldCorrection, SetOrigin, WarpImageMultiTransform, AverageImages, AverageAffineTransform, and MultiplyImages.`

## Prepare to run ANTS on a single subject using Condor.

In order to run ANTS repeatedly on a number of subjects, we will have to run it multiple times on a single subject. Once you are done, you should be able to run it like this

```bash
go_ants_nifti.sh templateFile.nii inputFile.nii outputFile.nii maskFile.nii
```

This script will intensity normalize, bias correct, and zero the origin of both test and template images, then run image registration from test to template.

**Bash script to run ANTS on one brain.** — `go_ants_nifti.sh` ([download](/downloads/code/condor_ants/go_ants_nifti.sh))

```bash
#!/usr/bin/env bash

# Organize my executables.
mkdir ants
mv ./ImageMath ants/
mv ./N3BiasFieldCorrection ants/
mv ./SetOrigin ants/
mv ./ANTS ants/
mv ./WarpImageMultiTransform ants/

# Make sure my executables can be executed.
chmod -R a=wrx ants

# Setup the environment
export HOME=/home/`whoami`
export PATH=$PWD/ants:$PATH

# Rename my inputs.
mv $4 templateMask.nii

# Normalize the range of the two nifti files.
ImageMath 3 ./ants/templateImage.nii Normalize $1
ImageMath 3 ./ants/testImage.nii Normalize $2

# Bias correct the images.
N3BiasFieldCorrection  3 ./ants/templateImage.nii ./ants/templateImage_repaired.nii 4
N3BiasFieldCorrection  3 ./ants/testImage.nii ./ants/testImage_repaired.nii 4

# Ensure the origin is zero in all images.
SetOrigin 3 ./ants/templateImage_repaired.nii ./ants/templateImage_repaired.nii 0 0 0
SetOrigin 3 ./ants/testImage_repaired.nii  ./ants/testImage_repaired.nii 0 0 0

# Run ANTS!
ANTS 3 -m CC[./ants/templateImage_repaired.nii,./ants/testImage_repaired.nii, 1,2,-0.95] -t SyN[.10] -r Gauss[2,1] -o $3 -i 100x75x75x50 --use-Histogram-Matching --number-of-affine-iterations 10000x10000x10000x10000x10000 --MI-option 32x16000
# If you want to perform your registration using a weighted mask in tempalte space, you can add '-x templateMask.nii' to the end of the previous line.

# Create testImage in template space.
WarpImageMultiTransform 3 ./ants/testImage_repaired.nii $3 -R $1 ${3/\.nii/}Warp.nii ${3/\.nii/}Affine.txt
```

Once you have the script, you can create a submit file for your script. Each submit file describes an executable that can be run on a number of different input files. In this case, the submit file will describe how to run the script that we just looked at, `go_ants_nifti.sh`. These core components of a submit file are the `executable`, `transfer_input_files`, `transfer_output_files` and `Arguments` lines. These lines specify what files you will need to upload, what command to run, and what files to transfer back to your computer upon completion.

In addition to these basic processes, this submit file has a few lines that will help you out…

- document your success and failure (i.e. `Log`, `Output` and `Error` files).
- help your script run on the right computers (i.e. `Requirements`, `request_cpus`, `request_memory` `request_disk`).
- and, manage your job a bit by restarting it if it takes too long or gets booted from the compute-node unexpectedly (i.e. `periodic_hold`, `periodic_release`).

**Submit File to run go_ants_nifti.sh** — `go_ants_nifti.submit` ([download](/downloads/code/condor_ants/go_ants_nifti.submit))

```text
# program to run
Executable = go_ants_nifti.sh

# save log, output and error files
Log = $(outputFile)_go_ants.log
Error = $(outputFile)_go_ants.error
Output = $(outputFile)_go_ants.output

# housekeping
Universe = vanilla
notification = never
should_transfer_files = yes
when_to_transfer_output = ON_EXIT

# Put the job on hold if it is taking longer than 5 hours...
periodic_hold = (JobStatus == 2) && ((CurrentTime - EnteredCurrentStatus) > (60 * 60 * 5))

# release any job that had an issue and got set to hold after 30 seconds, and run it on a different computer
periodic_release = (JobStatus == 5) && ((CurrentTime - EnteredCurrentStatus) > 30) && (NumSystemHolds < 10)
match_list_length = 5
requirements = (TARGET.Name =!= LastMatchName1)

# set some minimal requirements
Requirements  = ( OpSys == "LINUX" && Arch =="X86_64" )
request_cpus = 1
request_memory = 2000
request_disk = 1000000

# files to transfer to the execute node
transfer_input_files = ANTS,ImageMath,N3BiasFieldCorrection,SetOrigin,WarpImageMultiTransform,$(templateFile),$(inputFile),$(maskFile)

# files to transfer back when you are done
transfer_output_files = $(outputAffine), $(outputWarp), $(outputFile)

# command arguments to run...
Arguments = $(templateFile) $(inputFile) $(outputFile) $(maskFile)

Queue
```

Assuming you setup your files appropriately, you could, at least in theory, run

```bash
condor_submit go_ants_nifti.submit
```

## Create a study-specific template using Condor.

Once you have ANTS running, the next step will be to create your study-specific template. This step, will create a mean image of all subjects in template space and transform it based on the average transformation it took subjects to get to template space. We will use the same strategy we used above, namely write a script and a submit file that will manage that script.

```bash
go_shapeUpdateTemplate.sh templateFile.nii templateSpacePrefix templateMask.nii newTemplateMask.nii
```

**Bash script to create a study specific template.** — `go_shapeUpdateTemplate.sh` ([download](/downloads/code/condor_ants/go_shapeUpdateTemplate.sh))

```bash
#!/usr/bin/env bash

# Organize my executables.
mkdir ants
mv ./AverageImages ants/
mv ./SetOrigin ants/
mv ./MultiplyImages ants/
mv ./AverageAffineTransform ants/
mv ./WarpImageMultiTransform ants/

# Make sure my executables can be executed.
chmod -R a=wrx ants

# Setup the environment
export HOME=/home/`whoami`
export PATH=$PWD/ants:$PATH

# Rename commandline arguments.
template=$1
outputname=$2
oldMask=$3
newMask=$4
templateRoot=${template//\.nii/}

# set gradient-step constant.
gradientstep=-.15

# move existing transforms into a warps directory.
mkdir warps
mv *Warp.nii warps/
mv *Affine.txt warps/

# Create mean aligned image.
AverageImages 3 ${template} 1 ${outputname}*.nii

# Create mean warp to template space.
AverageImages 3 ${templateRoot}warp.nii 0 warps/${outputname}*Warp.nii

# Multiply warp by gradient-step constant.
MultiplyImages 3 ${templateRoot}warp.nii ${gradientstep} ${templateRoot}warp.nii

# delete template affine.
rm -f ${templateRoot}Affine.txt

# Create mean Affine Transform
AverageAffineTransform 3 ${templateRoot}Affine.txt warps/${outputname}*Affine.txt

# Move template based on the inverse of the mean warp files.
WarpImageMultiTransform 3 ${template} ${template} ${templateRoot}warp.nii ${templateRoot}warp.nii ${templateRoot}warp.nii ${templateRoot}warp.nii -R ${template}

# Move template mask based on the inverse of the mean warp.
SetOrigin 3 ${oldMask} ${oldMask} 0 0 0
WarpImageMultiTransform 3 ${oldMask} ${newMask} ${templateRoot}warp.nii ${templateRoot}warp.nii ${templateRoot}warp.nii ${templateRoot}warp.nii -R ${template}

# Cleanup.
rm -rf ants/
rm -rf warps/
rm -rf ${outputname}*.nii
```

Then you create the Submit file that manages this bash script. This submit file will tell condor how to run and manage the above `go_shapeUpdateTemplate.sh`. If you are so inclined, you can update this submit file with some of the `requirements`, `requests` or `periodic_` commands above. (I didn't because I don't have a really good idea how much memory/disk this process takes, and don't want to preemptively put it on hold.

**Submit file to run go_shapeUpdateTemplate.sh** — `go_shapeUpdateTemplate.submit` ([download](/downloads/code/condor_ants/go_shapeUpdateTemplate.submit))

```text
Executable = go_shapeUpdateTemplate.sh

Log = go_shapeUpdateTemplate.log
Error = go_shapeUpdateTemplate.error
Output = go_shapeUpdateTemplate.output

Universe = vanilla
notification = never
should_transfer_files = yes
when_to_transfer_output = ON_EXIT

Requirements  = ( OpSys == "LINUX" && Arch =="X86_64" )

transfer_input_files = SetOrigin,AverageImages,MultiplyImages,AverageAffineTransform,WarpImageMultiTransform,$(oldMask),$(RegisteredFiles),$(AffineFiles),$(WarpFiles)

transfer_output_files = $(templateFile),$(newMask)

Arguments = $(templateFile) toTemplate_ $(oldMask) $(newMask)

Queue
```

## Create your DAG parallel and dependent processes.

Now you have two scripts and two submit files for those scripts. The DAG you create will allow you run these commands in the right order on the right subjects. The format of the DAG file is pretty simple. For every job you run, you need to define what submit files to use, define any variables you want to pass to the submit file, and any dependencies it has.

```text
PARENT previousTemplateCreation CHILD myANTS
JOB myANTS  go_ants_nifti.submit
VARS myANTS templateFile=templateFile.nii inputFile=myInputFile.nii maskFile=myMaskFile.nii outputAffine=myOutputAffine.txt outputWarp=myOutputWarp.nii  outputFile=myOutput.nii
PARENT myANTS CHILD nextTemplateCreation
```

This code will run the job `myANTS`. It defines `myANTS` as a single instance of `go_ants_nifti.sh` using the `go_ants_nifti.submit` submit file, with the specified `VARS`, which could dictate what subject to run. Importantly, this script will not run `myANTS` until another job `previousTemplateCreation` has finished, and will wait to start `nextTemplateCreation` until `myANTS` has finished.

Because this can get crazy complicated when you have many subjects and repeated template creation iterations, I wrote a bash script that will create a bunch of these commands.

**Create a Condor DAG file** — `createAntsDag_nifti.sh` ([download](/downloads/code/condor_ants/createAntsDag_nifti.sh))

```bash
#!/bin/bash
# USAGE: createAntsDag_nifti.sh template.nii templateMask.nii subject*.nii > ants_condor.dag

NUM_ITERATIONS=4;
TemplateFile=$1
TemplateImageMask=$2

shift 2
MyImages=`ls $*`

TemplateImage=$TemplateFile
TemplateRoot=${TemplateFile//\.nii/};

iterationCount=1;
while [ $iterationCount -le $NUM_ITERATIONS ]
do
    ouputFileList=""

    imageCount=0;
    for Image in $MyImages
    do

        ImageRoot=${Image//\.nii/};
        ImageFile=$ImageRoot.nii

        JobName="toTemplate_"$TemplateRoot"_"$iterationCount"Pass_"$ImageRoot

        outputFile=toTemplate_$ImageRoot.nii
        affineFile="toTemplate_"$ImageRoot"Affine.txt"
        warpFile="toTemplate_"$ImageRoot"Warp.nii"

        echo "Job $JobName go_ants_nifti.submit"
        echo "VARS $JobName templateFile=\"$TemplateImage\" inputFile=\"$ImageFile\" outputFile=\"$outputFile\" outputAffine=\"$affineFile\" outputWarp=\"$warpFile\" maskFile=\"$TemplateImageMask\" "

        outputFileList[$imageCount]=$outputFile
        outputAffineList[$imageCount]=$affineFile
        outputWarpList[$imageCount]=$warpFile
        JobList[$imageCount]=$JobName

        imageCount=$(( $imageCount + 1 ))

    done

    OldTemplateImageMask=""$TemplateImageMask
    TemplateImage=""$TemplateRoot"_"$iterationCount".nii";
    TemplateImageMask=""$TemplateRoot"_"$iterationCount"_mask.nii";

    if [ $iterationCount -ne 1 ]
    then
        parentIteration=$(( $iterationCount - 1 ))
        ParentJobName="createTemplate_"$TemplateRoot"_"$parentIteration
        echo "PARENT $ParentJobName CHILD ${JobList[@]}"
    fi

    JobName="createTemplate_"$TemplateRoot"_"$iterationCount
    echo "Job $JobName go_shapeUpdateTemplate.submit"
    echo "Parent ${JobList[@]} CHILD $JobName"
    outputFileListText=$(printf "%s," "${outputFileList[@]}")
    outputAffineListText=$(printf "%s," "${outputAffineList[@]}")
    outputWarpListText=$(printf "%s," "${outputWarpList[@]}")
    echo "VARS $JobName templateFile=\"$TemplateImage\" RegisteredFiles=\"${outputFileListText%?}\" AffineFiles=\"${outputAffineListText%?}\" WarpFiles=\"${outputWarpListText%?}\" oldMask=\"$OldTemplateImageMask\" newMask=\"$TemplateImageMask\" "

    iterationCount=$(( $iterationCount + 1 ))

done
```

Feel free to run it on your data and see what dag file it creates.

```bash
createAntsDag_nifti.sh template.nii templateMask.nii subject*.nii > myDag.dag
more myDag.dag
```

## Submit your DAG.

If you have gotten this far, you should be ready to submit your DAG file.

```bash
condor_submit_dag myDag.dag
```

Once you submit this file, your condor system should manage the execution of your script and give you many-many output files. In particular it should create a file for each `subject*.nii` in standard space called `toTemplate_subject*.nii`, as well as `toTemplate_subject*Affine.txt` and `toTemplate_subject*Warp.nii` files that describe the transformation. It will also create a study-specific template, called `template_4.nii`

Hopefully this will help you get your ANTSing to run faster.
