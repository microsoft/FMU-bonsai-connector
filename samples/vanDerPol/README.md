# FMU Example: Van der Pol

This simulator simulates a Van der Pol frequency response. It is not a steady-state simulator.
The brain will learn to 
learns to parametrize the correct input pipe pressure and diameter to drive the steady-state
simulation to a specific output value on "flow rate".

## States

| State         | Range            | Notes    |
| ------------- | ---------------- | -------- |
| x0            | [-Inf ... Inf]   | First direction of a Van der Pol system. |
| x1            | [-Inf ... Inf]   | Second position of a Van der Pol system. |
| derx0         | [-Inf ... Inf]   | Speed on first direction. |
| derx1         | [-Inf ... Inf]   | Speed on second direction. |

## Actions

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| x0_adjust           | [-0.2 ... 0.2]       | Adjustment on first direction of Van der Pol system. |

## Configuration Parameters

| State               | Range                | Notes    |
| ------------------- | -------------------- | -------- |
| mu                  | [0.5 ... 4]          | Oscillation parameter. |

## Setting up: Installation & Bonsai configuration

Go to this project's [README.md](../../README.md) to review:

- INSTALLATIONS REQUIRED (conda & setting environment up)
- SETTING UP BONSAI CONFIGURATION

## Running the model: Local simulator

Open an Anaconda Prompt window.

1. Point to the "samples" folder and get inside any of the proposed examples

2. Create a new brain and push INK file:

    > bonsai brain create -n vanDerPol_v0
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n vanDerPol_v0

3. Start simulator using:

    > python main.py

    - By default, you will have to verify the set of {inputs/outputs/config params} is correct.
    - Check the CMD Prompt to follow instructions.
    - The moment you answer 'y' once, the config will be validated
    - You can disable being prompted again by setting FIRST_TIME_RUNNING to False in main.py:

    > FIRST_TIME_RUNNING = False

4. Start brain training from CLI

    > bonsai brain version start-training -n vanDerPol_v0

5. Connect simulators to unmanaged local sim:

    > bonsai simulator unmanaged connect -b vanDerPol_v0 -a Train -c ReduceOscillation --simulator-name VanDerPol_Oscillations

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Scaling your simulator

Once you have confirmed input/outputs of the model through command prompt, you can go ahead and disable authentication.
Open [main.py](main.py) and set FIRST_TIME_RUNNING to False:

> FIRST_TIME_RUNNING = False

- This step ensures the image is not waiting for user input to start the simulation. Config file approved by user is used.
once variable is set to False. In our case the sim configuration should be located at:
[sim/vanDerPol.yaml](sim/vanDerPol_conf.yaml)

Then, on an Anaconda Prompt window

1. Go to the "samples\fm_RSM_FMU_Pipeline" folder

2. Create a new brain and push INK file:

    > bonsai brain create -n vanDerPol_v0
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n vanDerPol_v0

3. Log in into Azure and push image

    > az login
    > 
    > az acr build --image fmu_image_vanDerPol:1 --platform windows --file Dockerfile-windows --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

4. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image_vanDerPol:1

    - Simulator package display name:  fmu_image_vanDerPol_v1

5. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {_"fmu_image_vanDerPol_v1"_}"

** Check [adding a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other)
for further information about how to upload the container, add it to Bonsai, and scale the simulator.
