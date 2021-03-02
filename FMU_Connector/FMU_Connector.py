
from datetime import datetime
import shutil
import fmpy
from fmpy import *
import yaml
import re

from typing import Any, Dict, List, Union


SIM_CONFIG_NAME_f = lambda model_fp: model_fp.replace(".fmu", "_conf.yaml")

# [TODO] dynamically read FMI version from modelDescription.xml
# ("1.0", "2.0", "3.0")
FMI_VERSION = "2.0"

START_TIME = 0.0
STOP_TIME = 20.0
STEP_SIZE = 0.1


# [TODO] Track which object/attribute can inform of sim errors
#  > Add as a halt condition, and reset

class FMUSimValidation:
    def __init__(
        self,
        model_filepath: str,
        user_validation: bool = True,
    ):
        """Template for validating FMU models for Bonsai integration.

        Parameters
        ----------
        model_filepath: str
            Filepath to FMU model.
        user_validation: bool
            If True, model inputs/outputs need to be accepted by user for each run.
            If False, YAML config file is used (if exists and valid). Otherwise, FMI
              file is read. If FMI model description is also invalid, error is raised.
        """

        # ensure model filepath is balid, and save as att if it is
        assert model_filepath.endswith(".fmu"), "Provided filepath is not an FMU file: '{}'".format(model_filepath)
        self.model_filepath = model_filepath
        # config file with config_params, inputs, outputs
        self.sim_config_filepath = SIM_CONFIG_NAME_f(self.model_filepath)

        # read the model description
        self.model_description = read_model_description(model_filepath)
        error_log  = "Provided model ({}) doesn't have modelVariables in XLS description file".format(model_filepath)
        assert len(self.model_description.modelVariables) > 0, error_log

        # correct non-alphanumeric tags.
        # note, it doesn't suppose any problem, since interaction with sim uses indices, not names.
        self._clean_non_alphanumeric_chars()

        # collect the value references (indices)
        self.vars_to_idx = {}
        for variable in self.model_description.modelVariables:
            self.vars_to_idx[variable.name] = variable.valueReference #, variable.causality

        # initialize sim config
        self.is_model_config_valid = False  # Currently unused, since error is raised if model invalid
        self.sim_config_params = []
        self.sim_inputs = []
        self.sim_outputs = []
        self.sim_other_vars = []

        # ---------------------------------------------------------------------
        # YAML CONFIG --> check for existing config using SIM_CONFIG_NAME_f --> e.g: "{model_name}_conf.yaml"
        valid_config = self._validate_sim_config()
        
        # exit if model is valid, unless validation has been activated
        if valid_config:

            # print model config for user reference: config_params, inputs, outputs
            print(self._get_sim_config_str())

            if user_validation:
                # prompt user to manually validate model if selected
                validation_asserted = input("Is this configuration correct (y|n)? ")

                if validation_asserted == "y":
                    self.is_model_config_valid = True
                    return
                
                # reset config if invalid
                self.sim_config_params = []
                self.sim_inputs = []
                self.sim_outputs = []
                self.sim_other_vars = []
            
            else:
                # when no validation is selected, we assume the sim config is valid
                self.is_model_config_valid = True
                return
            
        # ---------------------------------------------------------------------
        # FMI CONFIG --> if model is invalid we look for attributes within the .fmi model definition
        valid_config = self._extract_sim_config_from_fmi_std()

        if valid_config:

            # print model config for user reference: config_params, inputs, outputs
            print(self._get_sim_config_str())
            
            if user_validation:
                # prompt user to manually validate model if selected
                validation_asserted = input("Is this configuration correct (y|n)? ")

                if validation_asserted == "y":
                    self.is_model_config_valid = True
                    # dump YMAL file to reuse next time the model is loaded
                    self._dump_config_to_yaml_file()
                    return
            
            else:
                # when no validation is selected, we assume the sim config is valid
                self.is_model_config_valid = True
                # dump YMAL file to reuse next time the model is loaded
                self._dump_config_to_yaml_file()
                return
            
            # Dump auxiliary YAML config file if user doesn't assert the provided set
            #   of config_params/inputs/outputs
            self._dump_config_to_yaml_file(is_aux_yaml = True)
        
        # If neither YAML nor FMI model is sufficient raise error
        error_log  = "MODEL DOES NOT HAVE THE CORRECT CONFIG DEFINED NEITHER ON YAML CONFIG FILE "
        error_log += "NOR FMI MODEL DESCRIPTION."
        raise Exception(error_log)
        



    def _validate_sim_config(self):
        """Check if configuration file exists, otherwise indicate user to do so
            Configuration contains sim config_params/inputs/outputs and naming
            convention follows SIM_CONFIG_NAME_f --> e.g: "{modelname}_conf.yaml"

            > E.g:  filename == "cartpole.fmu"
               -->  config   == "cartpole_conf.yaml"
        """


        print("\n---- Looking to see if YAML config file exists ----")

        # use convention to search for config file
        config_file = self.sim_config_filepath
        print("config_file --> ", config_file)

        if os.path.isfile(config_file):
            print("Sim config file for selected example was found: {}\n".format(config_file))

            # Open and extract sim config from YAML file
            with open(config_file, 'r') as file:
                #data = yaml.dump(config_file, Loader=yaml.FullLoader)
                simulation_config = yaml.load(file, Loader=yaml.FullLoader)
            
            if 'simulation' not in simulation_config.keys():
                print("Configuration file for selected example does not have a 'simulation' tag, thus it is omited.")
                return False

            # Extract sim configuration from dict
            sim_config_params = simulation_config['simulation']['config_params']
            sim_inputs = simulation_config['simulation']['inputs']
            sim_outputs = simulation_config['simulation']['outputs']
            sim_other_vars = simulation_config['simulation']['other_vars']

            # Validate values extracted
            if len(sim_inputs) == 0:
                print("Sim config file has no sim-input states, and thus cannot be used\n")
            elif len(sim_outputs) == 0:
                print("Sim config file has no sim-output states, and thus cannot be used\n")
            else:
                # Store data extracted as attributes
                self.sim_config_params = sim_config_params
                self.sim_inputs = sim_inputs
                self.sim_outputs = sim_outputs
                self.sim_other_vars = sim_other_vars
                return True
        
        else:
            print("Configuration file for selected example was NOT found: {}".format(config_file))

        return False

    
    def _extract_sim_config_from_fmi_std(self):
        """We use the fmi standard to extract the correct set of config_params, inputs, outputs
            We look into the "causality" attribute for each variable in model description

            > E.g:  {var}.causality == "parameter"  ==>  sim config_params
                    {var}.causality == "input"      ==>  sim inputs
                    {var}.causality == "output"     ==>  sim outputs
        """
        
        print("\n---- Looking to see if FMU model description contains required 'causality' type definitions ----")

        sim_config_params = []
        sim_inputs = []
        sim_outputs = []
        sim_other_vars = []
        for variable in self.model_description.modelVariables:

            # extract causality and append valu
            causality = variable.causality

            if causality == "parameter":
                sim_config_params.append(variable.name)
            elif causality == "input":
                sim_inputs.append(variable.name)
            elif causality == "output":
                sim_outputs.append(variable.name)
            else:
                sim_other_vars.append(variable.name)
        
        # Validate values extracted
        if len(sim_inputs) == 0:
            print("\nSim FMU description file has no sim-input states, and thus cannot be used.")
        elif len(sim_outputs) == 0:
            print("\nSim FMU description file has no sim-output states, and thus cannot be used.")
        else:
            # Store data extracted as attributes
            self.sim_config_params = sim_config_params
            self.sim_inputs = sim_inputs
            self.sim_outputs = sim_outputs
            self.sim_other_vars = sim_other_vars
            return True


        # Dump auxiliary YMAL file for user to review/edit
        self._dump_config_to_yaml_file(sim_config_params,
                                       sim_inputs,
                                       sim_outputs,
                                       sim_other_vars,
                                       is_aux_yaml = True)

        return False

    
    def _dump_config_to_yaml_file(self,
                                  sim_config_params = None,
                                  sim_inputs = None,
                                  sim_outputs = None,
                                  sim_other_vars = None,
                                  is_aux_yaml = False):
        """Dump sim's config_params, inputs, and outputs to YAML file
             By default, we overwrite to main YAML config file.
        
        sim_other_vars: str
            If provided.
        """

        if sim_config_params is None:
            sim_config_params = self.sim_config_params
        if sim_inputs is None:
            sim_inputs = self.sim_inputs
        if sim_outputs is None:
            sim_outputs = self.sim_outputs
        if sim_other_vars is None:
            sim_other_vars = self.sim_other_vars

        if not is_aux_yaml:
            config_file = self.sim_config_filepath
        else:
            config_file = self.sim_config_filepath.replace(".yaml", "_EDIT.yaml")

        # Prepare set of unused data ( to be shared with user for editing )
        full_sim_config = {"config_params": sim_config_params,
                           "inputs": sim_inputs,
                           "outputs": sim_outputs,
                           "other_vars": sim_other_vars}
        full_sim_data = {"simulation": full_sim_config}

        # Dump configuration to YAML file for later reuse (or user editing if "is_aux_yaml==True")
        with open(config_file, 'w') as file:
            dump = yaml.dump(full_sim_data, sort_keys = False, default_flow_style=False)
            file.write( dump )

        # Raise error, and avoid continuing using model
        log  = "\nA YAML file with bonsai required fields, as well as available "
        log += "sim variables, has been dumped to: \n   --> '{}'\n".format(config_file)
        
        if is_aux_yaml:
            log += "Edit the YAML file, and remove the '_EDIT' nametag to use this model."
        
        print(log)

        return

    
    def _get_sim_config_str(self):
        """Get string with the sim's config_params, inputs, and outputs for the model
        """

        log  = "The found set of configuration_parameters, inputs, and outputs is the following:\n"
        log += "\n{}:  {}".format("Sim Config Params  --  Brain Config      ", self.sim_config_params)
        log += "\n{}:  {}".format("Sim Inputs         --  Brain Actions     ", self.sim_inputs)
        log += "\n{}:  {}".format("Sim Outputs        --  Brain States      ", self.sim_outputs)
        log += "\n{}:  {}".format("Sim Other Vars     --  Other Sim States  ", self.sim_other_vars)
        
        return log


    def _clean_non_alphanumeric_chars(self):
        """Remove non-alphanumeric characters to make them valid with Bonsai interaction.
        """

        self.var_to_idx = {}
        for i,variable in enumerate(self.model_description.modelVariables):
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', variable.name)
            if clean_name != variable.name:
                log = "Sim variable '{}' has been renamed to '{}' ".format(variable.name, clean_name)
                log += "to comply with Bonsai naming requirements."
                print(log)
            self.model_description.modelVariables[i].name = clean_name

        return



class FMUConnector:
    def __init__(
        self,
        model_filepath: str,
        fmi_version: str = FMI_VERSION,
        start_time = START_TIME,
        stop_time = STOP_TIME,
        step_size = STEP_SIZE,
        user_validation: bool = False,
    ):
        """Template for simulating FMU models for Bonsai integration.

            Note, it calls FMUSimValidation to validate the model when first instanced.

        Parameters
        ----------
        model_filepath: str
            Filepath to FMU model.
        fmi_version: str
            FMI version (1.0, 2.0, 3.0).
              [TODO] Automate reading value from model_description.
                <fmiModelDescription> tag is not accessible from model_description.
        start_time: float
            Timestep to start the simulation from (in time units).
        stop_time: float
            Timestep to stop simulation (in time units).
        step_size: float
            Time to leave the simulation running in between steps (in time units).
        user_validation: bool
            If True, model inputs/outputs need to be accepted by user for each run.
            If False, YAML config file is used (if exists and valid). Otherwise, FMI
              file is read. If FMI model description is also invalid, error is raised.
        """

        # validate simulation: config_vars (optional), inputs, and outputs
        validated_sim = FMUSimValidation(model_filepath, user_validation)
        
        # extract validated sim configuration
        self.model_filepath = validated_sim.model_filepath
        self.sim_config_filepath = validated_sim.sim_config_filepath
        self.model_description = validated_sim.model_description
        self.sim_config_params = validated_sim.sim_config_params
        self.sim_inputs = validated_sim.sim_inputs
        self.sim_outputs = validated_sim.sim_outputs
        self.sim_other_vars = validated_sim.sim_other_vars

        # get model name
        self.model_name = os.path.basename(self.model_filepath).replace(".fmu", "")
        # placeholder to prevent accessing methods if initialization hasn't been called first
        self._is_initialized = False
        
        # get FMI version
        assert fmi_version in ["1.0", "2.0", "3.0"], "fmi version provided ({}) is invalid.".format(fmi_version)
        self.fmi_version = fmi_version #[TODO] Review:: self.model_description.fmiModelDescription.fmiVersion
        
        # save time-related data
        error_log = "Stop time provided ({}) is lower than start time provided ({})".format(stop_time, start_time)
        assert stop_time > start_time, error_log
        error_log  = "Step size time ({}) is greater than the difference between ".format(step_size)
        error_log += "stop and start times, ({}) and ({}), respectively".format(stop_time, start_time)
        assert step_size < stop_time-start_time, error_log
        self.start_time = float(start_time)
        self.stop_time = float(stop_time)
        self.step_size = float(step_size)
        self.sim_time = float(self.start_time)
        
        # retrieve FMU model type, as well as model identifier
        self.model_type = "None"
        self.model_identifier = self.model_name
        modelExchange = self.model_description.modelExchange
        if modelExchange is not None:
            self.model_identifier = modelExchange.modelIdentifier
            self.model_type = "modelExchange"
        else:
            coSimulation = self.model_description.coSimulation
            if coSimulation is not None:
                self.model_identifier = coSimulation.modelIdentifier
                self.model_type = "coSimulation"
            else:
                scheduledExecution = self.model_description.scheduledExecution
                if scheduledExecution is not None:
                    self.model_identifier = scheduledExecution.modelIdentifier
                    self.model_type = "scheduledExecution"
                else:
                    raise Exception("Model is not of any known type: coSimulation, scheduledExecution, nor modelExchange")
        

        # collect the value references (indices)
        self.var_to_idx = {}
        for variable in self.model_description.modelVariables:
            self.var_to_idx[variable.name] = variable.valueReference

        # collect vars that need to be initialized before running
        self.vars_to_be_initialized = {}
        for variable in self.model_description.modelVariables:
            # Addditional notes:
            # - variable.start <==> variable.initial != "calculated"
            # - variable.start <==> variable.initial == "approx" or "exact"
            if variable.start is not None:
                # We assume all variables will be float from now
                # [TODO] Handle other variable types (read type from modelDescription.xls)
                self.vars_to_be_initialized[variable.name] = float(variable.start)

        
        # extract the FMU
        self.unzipdir = extract(self.model_filepath)

        # get unique identifier using timestamp for instance_name (possible conflict with batch)
        self.instance_name = self._get_unique_id()
        

        # ---------------------------------------------------------------
        # instance model depending on 'fmi version' and 'fmu model type'
        self.fmu = None
        if self.model_type == "modelExchange":
            ## [TODO] test integrations
            if self.fmi_version == "1.0":
                self.fmu = fmi1.FMU1Model(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
            elif self.fmi_version == "2.0":
                self.fmu = fmi2.FMU2Model(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
            elif self.fmi_version == "3.0":
                self.fmu = fmi3.FMU3Model(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
        elif self.model_type == "coSimulation":
            if self.fmi_version == "1.0":
                ## [TODO] test integrations
                self.fmu = fmi1.FMU1Slave(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
            elif self.fmi_version == "2.0":
                self.fmu = fmi2.FMU2Slave(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
            elif self.fmi_version == "3.0":
                ## [TODO] test integrations
                self.fmu = fmi3.FMU3Slave(guid=self.model_description.guid,
                                          unzipDirectory=self.unzipdir,
                                          modelIdentifier=self.model_identifier,
                                          instanceName=self.instance_name)
        elif self.model_type == "scheduledExecution":
            if self.fmi_version == "1.0" or self.fmi_version == "2.0":
                raise Exception("scheduledExecution type only exists in fmi_v3, but fmi version '{}' was provided.".format(self.fmi_version))
            
            ## [TODO] test integrations
            #elif self.fmi_version_int == 3:
            self.fmu = fmi3.FMU3ScheduledExecution(guid=self.model_description.guid,
                                                   unzipDirectory=self.unzipdir,
                                                   modelIdentifier=self.model_identifier,
                                                   instanceName=self.instance_name)
        
        
        # ---------------------------------------------------------------
        return


    def initialize_model(self, config_param_vals = None):
        """Initialize model in the sequential manner required.
            [TODO] Add config initialization here.
        """
        self._is_initialized = True

        self.fmu.instantiate()
        self.fmu.reset()
        self.fmu.setupExperiment(startTime=self.start_time)
        if config_param_vals is not None:
            self._apply_config(config_param_vals)
        self.fmu.enterInitializationMode()
        self.fmu.exitInitializationMode()

        return

    
    def run_step(self):
        """Move one step forward.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("run_step")

        # Check if sim is steady-state (doesn't contain "doStep" method)
        if  "doStep" not in dir(self.fmu):
            error_log  = "[run_step] FMU model cannot be run one step-forward, since it is a steady-state sim. "
            error_log += "No step advance will be applied."
            print(error_log)
            return

        self.fmu.doStep(currentCommunicationPoint=self.sim_time, communicationStepSize=self.step_size)
        self.sim_time += self.step_size
        return

    
    def reset(self, config_param_vals: Dict[str, Any] = None):
        """Reset model with new config (if given).
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("reset")

        # Terminate and re-initialize
        self.fmu.terminate()
        self.initialize_model(config_param_vals)
        return

    
    def close_model(self):
        """Close model and remove unzipped model from temporary folder.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("close_model")

        # [TODO] perform 'terminate' check prior to applying termination.
        # otherwise, an error is raised.
        #self.fmu.terminate()

        # free fmu
        self.fmu.freeInstance()
        # clean up
        # [TODO] enforce clean up even when exceptions are thrown, or after keyboard interruption
        shutil.rmtree(self.unzipdir, ignore_errors=True)
        return
        

    
    def get_states(self, sim_outputs: List = None):
        """Get var indices for each (valid) var name provided in list.
             If none are provided, all outputs are returned.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("get_states")

        if sim_outputs is None:
            sim_outputs = self.sim_outputs
        elif not len(sim_outputs) > 0:
            sim_outputs = self.sim_outputs

        states_dict = self._get_variables(sim_outputs)
        
        # Check if more than one index has been found
        if not len(states_dict.keys()) > 0:
            print("[get_states] No valid state names have been provided. No states are returned.")
            return {}

        return states_dict

    
    def apply_actions(self, b_action_vals: Dict[str, Any] = {}):
        """Apply brain actions to simulation inputs.

        b_action_vals: dict
            Dictionary of brain (action_name, action_value) pairs.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("apply_actions")

        # Ensure action dict is not empty
        if not len(b_action_vals.items()) > 0:
            print("[apply_actions] Provided action dict is empty. No action changes will be applied.")
            return False
        
        # We forward the configuration values provided
        applied_actions_bool = self._set_variables(b_action_vals)

        if not applied_actions_bool:
            print("[apply_actions] No valid action parameters were found. No actions applied.")

        return applied_actions_bool


    def get_all_vars(self):
        """Get a dictionary of (var_name: var_val) pairs for all variables in simulation.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("get_all_vars")

        # Get all variable names in model
        all_var_names = self.get_all_var_names()

        # Reusing get_states method --> Retrieve dict with (state_name, state_value) pairs
        all_vars = self.get_states(all_var_names)
        return all_vars


    def get_all_var_names(self):
        """Get a list of all variables in the sim (removing duplicates, if any).
             Note, list is kept the same from first time this method is called.
        """

        if hasattr(self, "all_var_names"):
            return self.all_var_names

        # Append all variables in model (defined in YAML).
        aux_all_var_names = []
        aux_all_var_names.extend(self.sim_config_params)
        aux_all_var_names.extend(self.sim_inputs)
        aux_all_var_names.extend(self.sim_outputs)
        aux_all_var_names.extend(self.sim_other_vars)

        # Remove duplicates (if any) -- Keeping initial order
        all_var_names = [aux_all_var_names[i] for i in range(len(aux_all_var_names)) \
                      if aux_all_var_names[i] not in aux_all_var_names[:i]]

        # Store for following calls
        self.all_var_names = all_var_names
        return self.all_var_names


    def _apply_config(self, config_param_vals: Dict[str, Any] = {}):
        """Apply configuration paramaters.
        """

        # Ensure array is not empty
        if not len(config_param_vals.items()) > 0:
            print("[_apply_config] Config params was provided empty. No changes applied.")
            return False
        
        # We forward the configuration values provided
        applied_config_bool = self._set_variables(config_param_vals)
            
        # Report config application to user
        if not applied_config_bool:
            print("[_apply_config] No valid config parameters were found. No changes applied.")

        # Take of any other variables that require initialization
        print("[_apply_config] Apply additional required initializations.")
        non_initialized_vars = [var_tuple for var_tuple in self.vars_to_be_initialized.items() \
                                          if var_tuple[0] not in config_param_vals.keys()]
        vars_to_initialize_d = dict(non_initialized_vars)
        applied_init_bool = self._set_variables(vars_to_initialize_d)
            
        # Report additional initializations to user
        if applied_init_bool:
            log = "[_apply_config] Initialized the following required values to "
            log += "FMU defaults: ({}).".format(vars_to_initialize_d)
            print(log)

        return applied_config_bool

    
    def _get_variables(self, sim_outputs: List = None):
        """Get var indices for each (valid) var name provided in list.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("_get_variables")

        # Ensure array is not empty
        if sim_outputs is None:
            return {}
        elif not len(sim_outputs) > 0:
            #print("[_get_variables] No var names were provided. No vars are returned.")
            return {}


        sim_output_indices, sim_output_names = self._var_names_to_indices(sim_outputs)
        
        # Check if more than one index has been found
        if not len(sim_output_indices) > 0:
            #print("[_get_variables] No valid var names have been provided. No vars are returned.")
            return {}
        
        outputs_dict = dict(zip(sim_output_names, self.fmu.getReal(sim_output_indices)))

        return outputs_dict

    
    def _set_variables(self, b_input_vals: Dict[str, Any] = {}):
        """Apply given input values to simulation.

        b_input_vals: dict
            Dictionary of brain (input_name, input_value) pairs.
        """
        
        # Ensure model has been initialized at least once
        self._model_has_been_initialized("_set_variables")

        # Ensure dict is not empty
        if not len(b_input_vals.items()) > 0:
            #print("[_set_variables] Provided input dict is empty. No input changes will be applied.")
            return False
        
        # Get input names, and extract indices
        sim_inputs = list(b_input_vals.keys())
        sim_input_indices,sim_input_names = self._var_names_to_indices(sim_inputs)
        
        # Check if more than one index has been found
        if not len(sim_input_indices) > 0:
            #print("[_set_variables] No valid input names have been provided. No input changes will be applied.")
            return False

        # Extract values for valid inputs (found on model variables)
        sim_input_vals = [b_input_vals[sim_input_name] for sim_input_name in sim_input_names]

        # Update inputs to the brain
        self.fmu.setReal(sim_input_indices, sim_input_vals)

        return True

    
    def _var_names_to_indices(self, var_names: List):
        """Get var indices for each var name provided in list.
        """

        if type(var_names) is not type([]):
            # Return empty array if input is not 'list' type
            print("[_var_names_to_indices] Provided input is not of type list.")
            return []

        indices_array = []
        names_array = []
        for name in var_names:
            if name not in self.var_to_idx.keys():
                print("[_var_names_to_indices] Invalid variable name '{}' has been skipped.".format(name))
                continue
            indices_array.append(self.var_to_idx[name])
            names_array.append(name)

        if not len(var_names) > 0:
            print("[_var_names_to_indices] No (valid) states have been provided.")

        return indices_array, names_array


    def _get_unique_id(self):
        """Get unique id for instance name (identifier).
        """
        now = datetime.now()

        u_id = now.second + 60*(now.minute + 60*(now.hour + 24*(now.day + 31*(now.month + 366*(now.year)))))
        return "instance" + str(u_id)


    def _model_has_been_initialized(self, method_name: str = ""):
        """Ensure model has been initialized at least once.
        """

        if not self._is_initialized:
            error_log  = "Please, initialize the model using 'initialize_model' method, prior "
            error_log += "to calling '{}' method.".format(method_name)
            raise Exception(error_log)

        