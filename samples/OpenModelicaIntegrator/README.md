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

***Note, this example only runs in win64***

## Running the model: Local simulator

Open an Anaconda Prompt window.

1. Activate Anaconda environment:

        conda activate fmu_env

2. Point to the "samples" folder and get inside any of the proposed examples

3. Create a new brain and push INK file:

        bonsai brain create -n OpenModelicaIntegrator_v0
        bonsai brain version update-inkling -f machine_teacher.ink -n OpenModelicaIntegrator_v0

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

        bonsai brain version start-training -n OpenModelicaIntegrator_v0

7. Connect simulators to unmanaged local sim:

        bonsai simulator unmanaged connect -b OpenModelicaIntegrator_v0 -a Train -c ReachTarget --simulator-name OpenModelicaIntegrator

If the simulation is running successfully, command line output should print "Registered simulator".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

## Running the model: Scaling your simulator

Once you have confirmed input/outputs of the model through command prompt, you can go ahead and disable authentication.
Open [main.py](main.py) and set FIRST_TIME_RUNNING to False (remember to set this to False, when transferring this examples to new models):

> FIRST_TIME_RUNNING = False

- This step ensures the image is not waiting for user input to start the simulation. Config file approved by user is used.
once variable is set to False. In our case the sim configuration should be located at:
[sim/OpenModelicaIntegrator_conf.yaml](sim/Integrator_conf.yaml)

Then, on an Anaconda Prompt window

1. Go to the "samples\OpenModelicaIntegrator" folder

2. Create a new brain and push INK file:

        bonsai brain create -n OpenModelicaIntegrator_v0
        bonsai brain version update-inkling -f machine_teacher.ink -n OpenModelicaIntegrator_v0

3. Go back to FMU-bonsai-connector root
4. Log in into Azure and push image

       az login
       az acr build --image fmu_image_open_modelica_integrator:1 --platform windows --file Dockerfile-windows_OpenModelicaIntegrator --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

    *Also, feel free to rerun before troubleshooting if you find the following error:
        
    > "container XXX encountered an error during hcsshim::System::Start: context deadline exceeded
    >
    > 2021/03/20 02:10:06 Container failed during run: build. No retries remaining.
    >
    > failed to run step ID: build: exit status 1

5. Go to preview.bons.ai
6. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image_OpenModelicaIntegrator:1

    - Simulator package display name:  fmu_image_OpenModelicaIntegrator_v1

    - OS: Windows

7. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {_"fmu_image_OpenModelicaIntegrator_v1"_}"

** Check [adding a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other)
for further information about how to upload the container, add it to Bonsai, and scale the simulator.

