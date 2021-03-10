# Flomaster Pipeline

This simulator simulates the flow of water within a pipe. It is a steady-state simulator.
There are no steps involved in this simulator per se. What this example seeks is that the brain
learns to find the correct actions to drive the steady-state simulation to a specific
output value on "flow rate".

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

NONE

## Setting up: Installation & Bonsai configuration

Go to this project's README.md to review:

- INSTALLATIONS REQUIRED (conda & setting environment up)
- SETTING UP BONSAI CONFIGURATION

## Usage: Running a local simulator

Open an Anaconda Prompt window.

1. Point to the "samples" folder and get inside any of the proposed examples

2. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_flomaster_v0
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_flomaster_v0

3. Start simulator using:

    > python main.py

4. Connect simulators to unmanaged local sim:

    > bonsai simulator unmanaged connect -b fmu_brain_v0 -a Train -c ReachTargetPipeflow --simulator-name FlomasterPipeline


If the simulation is running successfully, command line output should show "Sim successfully registered".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

> [TODO] Optional: Does the connector for FMU allow an integrated way of launching a local simulator, debugging a local simulator, or visualizing a local simulator as it executes via a user interface inside FMU? Such capabilities can be described here.

## Usage: Scaling your simulator

Open an Anaconda Prompt window.

1. Go to the "samples" folder and get inside any of the proposed examples

2. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_flomaster_v1
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_flomaster_v1

3. Log in into Azure and push image

    > az login
    > 
    > az acr build --image fmu_image_flomaster:1 --file Dockerfile --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

4. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image_flomaster:1

    - Simulator package display name:  fmu_image_flomaster_v1

5. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {"fmu_image_flomaster_v1"}"

** Check [adding a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other)
for further information about how to upload the container, add it to Bonsai, and scale the simulator.

> [TODO] Optional: Does the connector for FMU allow an integrated way of uploading a simulator to the Bonsai service or scaling the simulator instances for training via a user interface inside FMU? Such capabilities can be described here.

