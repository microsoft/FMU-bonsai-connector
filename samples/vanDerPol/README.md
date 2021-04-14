# FMU Example: Van der Pol

This simulator simulates a Van der Pol frequency response. It is not a steady-state simulator.
The brain will learn to adjust an input parameter to control the oscillator.

The simulator is implemented by [vanDerPol.fmu](https://github.com/modelica/fmi-cross-check/blob/master/fmus/2.0/cs/win64/FMUSDK/2.0.4/vanDerPol/vanDerPol.fmu) from the FMI Cross-Check repository.

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

## Configuration Parameters

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| mu                  | [0.5 ... 4]          | Oscillation parameter. |

This parameter will change the response of x1 to x0. Changing this parameter during training should further ensure we generalize to different scenarios (avoiding overfitting).

## Setting up: Installation & Bonsai configuration

Go to this project's [README.md](../../README.md) to review:

- INSTALLATIONS REQUIRED (conda & setting environment up)
- SETTING UP BONSAI CONFIGURATION

***Note, this example only runs in win64***

## Running the model: Local simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

        conda activate fmu_env

2. Point to the "samples" folder and get inside any of the proposed examples

3. Create a new brain and push INK file:

        bonsai brain create -n vanDerPol_v0
        bonsai brain version update-inkling -f machine_teacher.ink -n vanDerPol_v0

4. Start simulator using:

        python main.py

    - Note, for new examples, you will have to verify the set of {inputs/outputs/config params} is correct.
    - Check the CMD Prompt to follow instructions.
    - The moment you answer 'y' at least once, the config will be validated.
    - You can disable being prompted again by setting FIRST_TIME_RUNNING to False in main.py:

    > FIRST_TIME_RUNNING = False

5. Open a new Anaconda Prompt and activate the environment too

        conda activate fmu_env

6. Start brain training from CLI

        bonsai brain version start-training -n vanDerPol_v0

7. Connect simulators to unmanaged local sim:

        bonsai simulator unmanaged connect -b vanDerPol_v0 -a Train -c ReduceOscillation --simulator-name VanDerPol_Oscillations

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Scaling your simulator

Once you have confirmed input/outputs of the model through command prompt, you can go ahead and disable authentication.
Open [main.py](main.py) and set FIRST_TIME_RUNNING to False (remember to set this to False, when transferring this examples to new models):

> FIRST_TIME_RUNNING = False

- This step ensures the image is not waiting for user input to start the simulation. Config file approved by user is used.
once variable is set to False. In our case the sim configuration should be located at:
[sim/vanDerPol.yaml](sim/vanDerPol_conf.yaml)

Then, on an Anaconda Prompt window

1. Go to the "samples\vanDerPol" folder

2. Create a new brain and push INK file:

        bonsai brain create -n vanDerPol_v0
        bonsai brain version update-inkling -f machine_teacher.ink -n vanDerPol_v0

3. Go back to FMU-bonsai-connector root
4. Log in into Azure and push image

       az login
       az acr build --image fmu_image_vanderpol:1 --platform windows --file Dockerfile-windows_vanDerPol --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

    *Also, feel free to rerun before troubleshooting if you find the following error:
        
    > "container XXX encountered an error during hcsshim::System::Start: context deadline exceeded
    >
    > 2021/03/20 02:10:06 Container failed during run: build. No retries remaining.
    >
    > failed to run step ID: build: exit status 1

5. Go to preview.bons.ai
6. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image_vanDerPol:1

    - Simulator package display name:  fmu_image_vanderpol_v1

    - OS: Windows

7. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {_"fmu_image_vanderpol_v1"_}"

** Check [adding a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other)
for further information about how to upload the container, add it to Bonsai, and scale the simulator.

