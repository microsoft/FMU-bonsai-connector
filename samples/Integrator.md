# FMU Example: OpenModelica Integrator

This simulator uses the model Integrator.fmu. The source of the model is [IntegratorModel.mo](sim/IntegratorModel.mo), which was created with [OpenModelica](https://openmodelica.org/) and exported via FMI Co-Simuloation 2.0. This model adds the value of the action u (per second) to the state x.

## States

| State         | Range            | Notes    |
| ------------- | ---------------- | -------- |
| x             | [-Inf ... Inf]   | A numerical value. |

## Actions

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| u                   | [-Inf ... Inf]       | Change in x per second. |

## Configuration Parameters

none

## Setting up: Installation & Bonsai configuration

Go to this project's [README.md](../../README.md) to review:

- INSTALLATIONS REQUIRED (conda & setting environment up)
- SETTING UP BONSAI CONFIGURATION

> NOTE: This example only runs in win64.

## Running the model: Local simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

        conda activate fmu_env
        cd samples

2. Start simulator using:

        ./test-fmu.bat --mode local Integrator.fmu

3. Create brain and start training from the Bonsai CLI

        bonsai brain create -n Integrator
        bonsai brain version update-inkling -f Integrator.ink -n Integrator
        bonsai brain version start-training -n Integrator
        bonsai simulator unmanaged connect -b Integrator -a Train -c ReachTarget --simulator-name "Integrator FMU"

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Local simulator running in a Docker container

The steps for this are the same as for the previous scenario (Local simulator) except in step 2 start the simulator using:

        ./test-fmu.bat --mode local-container Integrator.fmu

## Running the model: Scaling your simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

        conda activate fmu_env
        cd samples

2. Build the simulator container and add it to your Bonsai workspace using:

        ./test-fmu.bat --mode managed Integrator.fmu

3. Create brain and start training from the Bonsai CLI

        bonsai brain create -n Integrator
        bonsai brain version update-inkling -f Integrator.ink -n Integrator
        bonsai brain version start-training -n Integrator --simulator-package-name Integrator_fmu
