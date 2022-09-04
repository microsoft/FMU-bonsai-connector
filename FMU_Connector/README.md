# FMU Connector: Class Explained

## - External Libraries -

This FMU Connector takes advantage of 2 auxiliary packages\libraries:

1. [Microsoft Bonsai API](https://github.com/microsoft/microsoft-bonsai-api)
- This API manages the connection to the Bonsai Azure Service. It enables the simulation registration towards training/assessing Bonsai brains.
- Library can be found at the following folder:
  >  FMU-bonsai-connector\FMU_Connector\microsoft-bonsai-api"

2. [FMPy](https://github.com/CATIA-Systems/FMPy)
- This library automates the interaction with FMU models following the [FMI Standard](https://fmi-standard.org/). It manages the low-level
interactions with simulations.

## - The FMU Connector -

The core part of the FMU Connector takes care of automating the interaction with FMUs using the FMPy library towards interacting with Bonsai
brains. The FMU abstracted class can be found at:
  > [FMU-bonsai-connector\FMU_Connector\FMU_Connector.py"](FMU_Connector.py)

Note, the part related to Bonsai Azure Service has been abstracted directly at the example-level, pretty much in the fashion of
microsoft-bonsai-api.

The FMU interaction consists of 2 classes:

- **FMUSimValidation**: Addresses FMU model validation. It prompts messages to the user as needed to verify the config params/inputs/outputs of the model.
  - The model makes use of the FMI standard as follows:
      > FMU_Model.fmu >> ModelDescription.xml >> ModelVariables >> ScalarVariable
      > > causality="parameter" --> Configuration parameters, and input to the simulation
      > > 
      > > causality="input" --> Brain actions, and input to the simulation
      > > 
      > > causality="output" --> Brain states, and output to the simulation
  - Nonetheless, to cope with those FMU models which might not have the correct configuration, we make use of an additional YAML file.
  This YAML file is directly used when found at the FMU directory level.
  - Model validation is very verbose intentionally, to ensure the user can access/modify the simulation configuration to fit their needs.

- **FMUConnector**: Takes care of automating the Bonsai workflow:
  - initialize_model:
    > Instances the model, providing the required config parameters. (*Note, default fmi values are used if none are given*)
  - run_step:
    > Advances the simulation one step forwasrd. (*Note, actions are applied separately*)
  - reset:
    > Terminates the simulation, and instances it back through "initialize_model".
  - close_model:
    > Frees FMU instance, and removes temporary unzipped folder created for FMU interaction.
  - get_states:
    > Returns the value for the requested variables. (*Note, any variable type can be requested*)
  - apply_actions:
    > Applies to the simulation the set of variable name/values sent as arguments to the method.
  - get_state_vars:
    > Retrieves the set of variables and values as a dictionary.


