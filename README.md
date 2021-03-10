# FMU connector

[TOREMOVE] ***Replace {SimPlatform} with the name of your simulation platform and fill out this template as described in the markdown files.***

A connector for integrating FMU models with [Microsoft Project Bonsai](https://azure.microsoft.com/en-us/services/project-bonsai/).
Note, FMUs are simulation units that follow the [FMI standard](https://fmi-standard.org/):

- Functional Mock-Up Interface (FMI) is a free standard that defines an interface to exchange dynamic models using a combination of XML files, binaries and C code.

## Requirements

The SDK supports the following versions of Python:

- Python 3 versions 3.7 and later

This FMU Connector takes advantage of 2 auxiliary packages*:

1. [Microsoft Bonsai API](https://github.com/microsoft/microsoft-bonsai-api) - This API manages the connection to the Bonsai Azure Service.

2. [FMPy](https://github.com/CATIA-Systems/FMPy) - This library automates the interaction with FMU models following the [FMI Standard](https://fmi-standard.org/).

*For more information check the readme at:
> FMU-bonsai-connector\FMU_Connector\README.md

## Installation

**Get Your Conda Environment Ready**

Create a new conda environment:

> conda create -n fmu_env python=3.7

Install required packages:

> conda env update -n fmu_env --file environment.yml

[TODO] Update "environment.yml" file with FMPy

## Setting up Bonsai configuration

Choose either of the following two approaches:

1. Set-up through environment variables (for all examples):

    - open File Explorer > right click over My PC > Properties > Advance System Settings > Advanced tab > Environment Variables...
    - Add bonsai config vars** clicking on "New..." under User variables:
    
      > SIM_WORKSPACE="abcdefgh-ijkl-lmno-pqrs-tuvwxyz12345"
      >
      > SIM_ACCESS_KEY="AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTT..."

2. Set-up through .env file (per example):

    - inside the example folder (where main.py is located), drop a .env file with the corresponding config vars**:
    
      > SIM_WORKSPACE="abcdefgh-ijkl-lmno-pqrs-tuvwxyz12345"
      >
      > SIM_ACCESS_KEY="AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTT..."

    - then, open 'main.py' and search for the following keyword "--config-setup"  -->  Set 'default' value to "True"

  ** Note, 'config vars' can be extracted from preview.bons.ai

## Usage: Running a local simulator

Open an Anaconda Prompt window.

1. Point to the "samples" folder and get inside any of the proposed examples

2. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_v0
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_v0

3. Start simulator using:

    > python main.py

4. Connect simulators to unmanaged local sim:

    > bonsai simulator unmanaged connect -b fmu_brain_v0 -a Train -c <concept_name> --simulator-name <sim_name>


If the simulation is running successfully, command line output should show "Sim successfully registered".
The Bonsai workspace should show the FMU simulator name under the Simulators section, listed as Unmanaged.

> [TODO] Optional: Does the connector for FMU allow an integrated way of launching a local simulator, debugging a local simulator, or visualizing a local simulator as it executes via a user interface inside FMU? Such capabilities can be described here.

## Usage: Scaling your simulator

Open an Anaconda Prompt window.

1. Go to the "samples" folder and get inside any of the proposed examples

2. Create a new brain and push INK file:

    > bonsai brain create -n fmu_brain_v1
    > 
    > bonsai brain version update-inkling -f machine_teacher.ink -n fmu_brain_v1

3. Log in into Azure and push image

    > az login
    > 
    > az acr build --image fmu_image:1 --file Dockerfile --registry <ACR_REGISTRY_NAME> .

    *Note, ACR Registry can be extracted from preview.bons.ai --> Workspace ACR path == <ACR_REGISTRY_NAME>.azurecr.io

4. Click over "Add Sim" > "Other", and insert the location of the image:

    - Azure Container Registry image path:  <ACR_REGISTRY_NAME>.azurecr.io/fmu_image:1

    - Simulator package display name:  fmu_sim_v1

5. Add package name to INK file:

    - Modify "source simulator Simulator([...]) \{ }" into "source simulator Simulator([...]) {"fmu_sim_v1"}"


** A link to the documentation topic [Add a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other) for information about how to upload the container, add it to Bonsai, and scale the simulator.

> [TODO] Optional: Does the connector for FMU allow an integrated way of uploading a simulator to the Bonsai service or scaling the simulator instances for training via a user interface inside FMU? Such capabilities can be described here.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
