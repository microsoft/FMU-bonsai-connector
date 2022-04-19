# FMU Connector

A connector for integrating FMU models with [Microsoft Project Bonsai](https://azure.microsoft.com/en-us/services/project-bonsai/).
Note, FMUs are simulation units that follow the [FMI standard](https://fmi-standard.org/):

- Functional Mock-Up Interface (FMI) is a free standard that defines an interface to exchange dynamic models using a combination of XML files, binaries and C code.

## Requirements

The SDK supports the following versions of Python:

- Python 3 versions 3.7 and later

**Each example might have additional requirements.** At this point, the examples covered by this connector require win64 processors.
Thus, they cannot run on Linux\Mac. If you run Linux or Mac, feel free to perform the scaled approach using a Windows image.

- These requirements exist due to the executables integrated within the model itself. They are extrinsic to Bonsai or this connector.

Lastly, note that this FMU Connector relies on 2 auxiliary packages*:

1. [Microsoft Bonsai API](https://github.com/microsoft/microsoft-bonsai-api) - This API manages the connection to the Bonsai Azure Service.

    - This software has been released under the same MIT License than this repository by the Bonsai team too.

2. [FMPy](https://github.com/CATIA-Systems/FMPy) - This library automates the interaction with FMU models following the [FMI Standard](https://fmi-standard.org/).

    > See [LICENSE_FMPY](LICENSE_FMPY) for License info.

*For more information check the readme at:
> [FMU-bonsai-connector\FMU_Connector\README.md](FMU_Connector/README.md)

## Setting up your environment

**Installing Anaconda**

For this project you will need to install [Anaconda](https://www.anaconda.com/products/individual) (or miniconda).
This software will take care of handling your virtual environments and packages installed.

**Installing Docker**

You will need Docker installed on your local machine. The community edition of Docker is available for Windows at https://docs.docker.com/engine/install.

> Docker runs in Linux mode by default. This FMU connector supports FMUs run with Windows. You will need to switch modes by right-clicking the Docker Desktop application in the notification area of the taskbar and selecting Switch to Windows containers.

**Get Your Conda Environment Ready**

    conda env create --file environment.yml
- A new environment called "fmu_env" should be ready to be used with any of the samples provided.

**Setting up Bonsai configuration**

Choose either of the following two approaches:

1. Set-up through .env file (per example):

    - inside the example folder (where main.py is located), drop a .env file with the corresponding bonsai config parameters**:
    
      > SIM_WORKSPACE="abcdefgh-ijkl-lmno-pqrs-tuvwxyz12345"
      >
      > SIM_ACCESS_KEY="AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTT..."

    - then, open 'main.py' and search for the following keyword "--config-setup"  -->  Set 'default' value to "True"

  ** Note, configuration parameters (workspace id & access key) should be retrieved from [preview.bons.ai](https://preview.bons.ai).
To drop them in a new .env file: (1) create a blank .txt file, (2) rename to .env, (3) drop your config params *(quotes included)*.

## Getting a new sim integrated

For setting up a new simulator follow the next steps:

1. Copy either of the example folders and rename to your own example name
2. Remove all files within the "sim" folder, and drop your FMU model
3. Upate [main.py](samples/vanDerPol/main.py) (read section bellow)
4. Update machine_teacher.ink
5. Update README.md before sharing/uploading your model

### Getting a new sim integrated: Update main.py

When setting up a new FMU model, you will have to get your hands dirty. But do not worry, we have simplified it for you.
We have added a set of "TODO_PER_SIM" tags to help you localize the 10 changes that need to be considered:

1. Define a version for FMI to be used by default in case FMU model lacks the correct variable (default "2.0")
2. Define if model should be run as a steady-state simulator (no time evolution involved)
3. Define Start, Stop, and Step Size in model's sim time units
4. Define default config in a dictionary - This will be used whenever none is configured on machine_teacher.ink
5. Set-up model filepath, as well as sim name to be displayed in preview.bons.ai
6. (optional) Modify states to be sent to Bonsai - By default we send all states
7. Add any action transformations required (from Bonsai to sim) -- if needed
8. Define any conditions when the simulation should be stopped
     - Note, halted episodes are thrown away unless terminated on INK too
9. Update the random policy to be used for the example on policies.py
10. Disabling authentication once you have validated model inputs/outputs/config params (displayed in command prompt)

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
