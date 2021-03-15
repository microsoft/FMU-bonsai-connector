# FMU Example: Flomaster Pipeline

This simulator simulates the flow of water within a pipe. It is a steady-state simulator.
There are no steps involved in this simulator per se. What this example seeks is that the brain
learns to parametrize the correct input pipe pressure and diameter to drive the steady-state
simulation to a specific output value on "flow rate".

## States

| State                    | Range            | Notes    |
| ------------------------ | ---------------- | -------- |
| Out Fluid Velocity       | [-Inf ... Inf]   | Speed at the other end of pipe. |
| Out Flow Rate            | [-Inf ... Inf]   | Volume of water going through end of pipe. |
| Out Pressure Drop        | [-Inf ... Inf]   | Pressure at the other end of the pipe. |

## Actions

| State                    | Range                | Notes    |
| ------------------------ | -------------------- | -------- |
| Inlet Pressure           | [50000 ... 100000]   | Pressure at the entrance of the pipe. |
| Pipe Diameter            | [0.2 ... 1.5]        | Diameter of the pipe. |

## Configuration Parameters

None for this example

## Setting up: Installation & Bonsai configuration

Go to this project's [README.md](../../README.md) to review:

- INSTALLATIONS REQUIRED (conda & setting environment up)
- SETTING UP BONSAI CONFIGURATION

***Note, this example only runs in win64***

## Running the model: Local simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

    > conda activate fmu_env

2. Point to the "samples" folder and get inside any of the proposed examples

3. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_flomaster_v0
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_flomaster_v0

4. Start simulator using:

    > python main.py

5. Open a new Anaconda Prompt and activate the environment too

    > conda activate fmu_env

6. Start brain training from CLI

    > bonsai brain version start-training -n fmu_brain_flomaster_v0

7. Connect simulators to unmanaged local sim:

    > bonsai simulator unmanaged connect -b fmu_brain_flomaster_v0 -a Train -c ReachTargetPipeflow --simulator-name FlomasterPipeline

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Scaling your simulator

Once you have confirmed input/outputs of the model through command prompt, you can go ahead and disable authentication.
Open [main.py](main.py) and set FIRST_TIME_RUNNING to False:

> FIRST_TIME_RUNNING = False

- This step ensures the image is not waiting for user input to start the simulation. Config file approved by user is used.
once variable is set to False. In our case the sim configuration should be located at:
[sim/fm_RSM_FMU_Pipeline_conf.yaml](sim/fm_RSM_FMU_Pipeline_conf.yaml)

Then, on an Anaconda Prompt window

1. Go to the "samples\fm_RSM_FMU_Pipeline" folder

2. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_flomaster_v1
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_flomaster_v1

3. Log in into Azure and push image

    > az login
    > 
    > az acr build --image fmu_image_flomaster:1 --platform windows --file Dockerfile-windows --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

4. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image_flomaster:1

    - Simulator package display name:  fmu_image_flomaster_v1

5. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {_"fmu_image_flomaster_v1"_}"

** Check [adding a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other)
for further information about how to upload the container, add it to Bonsai, and scale the simulator.

