# FMU Example: Van der Pol

This simulator simulates a Van der Pol frequency response.
The brain will learn to adjust an input parameter to control the oscillator.

The simulator is implemented by [vanDerPol.fmu](https://github.com/modelica/fmi-cross-check/blob/master/fmus/2.0/cs/win64/FMUSDK/2.0.4/vanDerPol/vanDerPol.fmu) from the FMI Cross-Check repository.
That vanDerPol.fmu model has been modified as follows:
* Added a DefaultExperiment with stepSize="0.1".
* Changed the causality of variable x0 to input so that x0 can be controlled by Bonsai actions.
* Changed the causality of variables x1, der(x0), and der(x1) to output so that they can be used as Bonsai states.

Note, this example will only run in a Windows environment, since it has Windows dependencies/executables inside the FMU model wrapper.

## States

| State         | Range            | Notes    |
| ------------- | ---------------- | -------- |
| x0            | [-Inf ... Inf]   | Main direction of oscillation of a Van der Pol system. |
| x1            | [-Inf ... Inf]   | Second direction of oscillation of a Van der Pol system. |
| derx0         | [-Inf ... Inf]   | Speed on first direction. |
| derx1         | [-Inf ... Inf]   | Speed on second direction. |

Note, the main behavior of a Van der Pol system is that x1, will oscillate with same magnitude than the speed in x0 (derx0).

## Actions

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| x0_adjust           | [-0.2 ... 0.2]       | Adjustment on first direction of Van der Pol system. |

In this Bonsai theoretical approach to the Van der Pol problem, it is assumed that we can perform small perturbations in only one of the directions (in x0).
The goal of the brain will be minimizing the oscillation as much as possible, adjusting to variable configuration parameters (see section bellow).

> NOTE: This FMU connector contains special logic in FMUSimulatorSession.episode_step that adds the value of x0_adjust to the previous value of x0.

## Configuration Parameters

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| mu                  | [0.5 ... 4]          | Oscillation parameter. |

This parameter will change the response of x1 to x0. Changing this parameter during training should further ensure we generalize to different scenarios (avoiding overfitting).

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

        ./test-fmu.bat --mode local vanDerPol.fmu

3. Create brain and start training from the Bonsai CLI

        bonsai brain create -n vanDerPol
        bonsai brain version update-inkling -f vanDerPol.ink -n vanDerPol
        bonsai brain version start-training -n vanDerPol
        bonsai simulator unmanaged connect -b vanDerPol -a Train -c ReduceOscillation --simulator-name "van der Pol oscillator FMU"

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Local simulator running in a Docker container

The steps for this are the same as for the previous scenario (Local simulator) except in step 2 start the simulator using:

        ./test-fmu.bat --mode local-container vanDerPol.fmu

## Running the model: Scaling your simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

        conda activate fmu_env
        cd samples

2. Build the simulator container and add it to your Bonsai workspace using:

        ./test-fmu.bat --mode managed vanDerPol.fmu

3. Create brain and start training from the Bonsai CLI

        bonsai brain create -n vanDerPol
        bonsai brain version update-inkling -f vanDerPol.ink -n vanDerPol
        bonsai brain version start-training -n vanDerPol --simulator-package-name vanDerPol_fmu
