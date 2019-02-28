.. _first_steps_overview:

==================
Tutorial: Overview
==================

This section gives an overview of the "mental model" behind the process around sequencing and demultiplexing from the point of view of Digestiflow.
It will describe the boundaries of the Digestiflow system and give examples what it does not attempt to support you with.
Further, it will introduce the different components of Digestiflow and how they support you in the sequencing and demultiplexing processes.

---------------------------
Processes Around Sequencing
---------------------------

The Digestiflow process model starts with the *sequencing* of *libraries* on certain *lanes on a flow cells*.
Digestiflow does **not**, e.g., consider your experimental design, help you in sample tracking, or with the storage or organization of your raw BCL or your produced FASTQ sequencing files.
It does also not help you with processing these files.

The authors consider such processe **external** to Digestiflow.
However, Digestiflow offers a REST API that can be used to connect external software components to the Digestiflow system.
For example, you could use the API to automatically fill the sample sheets based on the output of a barcode reader, or start ioinformatics processing such as read mapping.
It will be your task to integrate Digestiflow into your external processes.
Setting such clear boundaries allows Digestiflow to stay in a sweet spot of relative ease of use but also flexibility and allowing for integration with external services.

Overall, Digestiflow considers three steps:

1. Sequencing
2. Demultiplexing (or base call processing, e.g., to sequences or to base call archives)
3. Data Delivery

.. todo: add pictures with state automatons

------------------
Step 1: Sequencing
------------------

Generally, we find that *state machines* are a useful way to describe finite processes.
The Digestiflow Web component keeps track of your flow cell sequencing runs, the libraries thereon, and their states.
The states for sequencing are:

initial
    The system knows about the sequncing of a flow cell but the sequencing has not started yet.
running
    The sequencing device has started with the sequencing process.
complete
    The sequencing device finished and indicates that it detected no errors.
failed
    The sequencing device finished and indicates that it detected an error.
confirmed complete
    A human operator has inspected the sequencing output (e.g., the Illumina RTA and SVA results) for quality control (QC).
    They then deemed the results of passing QC.
confirmed complete with warnings
    A human operator has inspected the output and found some issues.
    The result is not considered a full QC failure but the results have to be treated with caution.
confirmed failure
    After inspection of the sequencing results, the operator decides that the results are generally unfit for future processing.
    Any further consideration, if any, of the data has to be done with extreme caution.

The *start states* are initial and running.
The initial state is triggered by a user manually registering the flow cell before the system has gained knowledge over a sequencing run.
This is done by entering it in the Digestiflow Web UI.

The running state is usually triggered by the Digestiflow CLI component.
This software can be setup as a watcher process and periodically scans the storage volume that the sequencing machine writes to.
As soon as it sees a new flow cell directory, it will register it with the Digestiflow Web API with the information that it can extract automatically.
In the case that the flow cell already exists, it will still update the flow cell information from the flow cell directory through the Digestiflow Web API, e.g., keeping track of the current cycle, or updating missing or incorrectly filled fields.

Digestiflow CLI then also keeps track of the further sequencing state as indicated by the status files in the flow cell directory.
By doing this, it is able to detect success (a marker file is created) and certain failures.
However, for certain critical technical failures such as issues with the storage volume or power failure in the sequencing lab cannot be easily detected.
Further, Digestiflow CLI will analyze the index adapters once their sequencing is complete and register statistics with Digestiflow Web UI.
This way, mismatches of the adapter base calls with the sample sheet can be detected already during sequencing.

Finally, Digestiflow CLI will update the state to complete or failed from which a human operator has to manually switch the sequencing to one of the final "confirmed" states.

----------------------
Step 2: Demultiplexing
----------------------

A filled sample sheet is the precondition for the demultiplexing of data.
This can be done after the sample sheet is known to the system, either by being added manually, or by being registered through Digestiflow CLI.
Once the sheet has been filled, the demultiplexing can start using Digestiflow Demux.
This component is also setup as a second watcher process to consider the sequencer run directories.

The demultiplexing states are as follows:

initial
    This is the default initial state.
ready
    After filling the sample sheet, the operator manually updates the state to "ready".
    This marks the flow cell to be ready for demultiplexing once the sequencing state is "complete" or one of the confirmed states.
running
    The demultiplexing process has been marked as running after being started.
complete
    The demultiplexing process has finished successfully and Digestiflow Demux has marked the state as "complete".
failed
    The demultiplexing process has failed for some reason and Digestiflow Demux has marked the state as "failed".
confirmed complete
    The demultiplexing operator has performed quality control of the demultiplexing results and considers them to pass the quality control.
confirmed failure
    The demultiplexing operator is unable to perform the demultiplexing correctly and marks it as failed.

Note that there is no "confirmed warning" state as this step assumes that discordances between the sample sheet and the libraries are resolved in the sample sheet.
By removing missing adapters from the sample sheet (and thus adjusting it to the experimental reality), and/or acknowledging any further mismatches, the sample sheet is put into consistency with the base calls.

Also note that Digestiflow offers to create tarball archives of the lanes instead of or in addition to the demultiplexing.
This is necessary as some sequencing facility customers/users prefer to start their pipelines from the BCL files.
Creating tarballs of individual lanes simplifies the extraction of the necessary per-flowcell and the desired per-lane information into one archive file.

---------------------
Step 3: Data Delivery
---------------------

Data delivery is considered a manual process.
The delivery operator performs the communication with the data recipient, sends the data in an appropriate way (e.g., a shared network volume), and finally confirms that the recipient received the data and the delivery is over.

initial
    Delivery does not have started.
in progress
    Files are being transferred or the operator is waiting for the recipient to confirm receiving the data.
complete
    The files have been delivered successfully.
skipped
    Delivery has been skipped as it is unnecessary, e.g., for test data internal to the sequencing facility.

Read on in the tutorial to learn about how Digestiflow supports you in these processes.
