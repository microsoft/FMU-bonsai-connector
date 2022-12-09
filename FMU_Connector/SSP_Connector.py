from fmpy import extract
from fmpy.ssp.ssd import System, read_ssd, get_connections, find_connectors, find_components, build_path, ParameterSet, Parameter
from fmpy.ssp.simulation import add_path, instantiate_fmu, do_step, free_fmu
from typing import Any, Dict, List, Union

verbose = False

class SSPConnector:
    def __init__(
        self,
        model_filepath: str
    ):
        self.model_filepath = model_filepath

        # extract the SSP
        self.ssp_unzipdir = extract(self.model_filepath)


    def initialize_model(self, config_param_vals = {}):
        self.error_occurred = False
        self.step_size = 0.01 # TODO: make this configurable and read default from ssp file or FMUs

        self.ssd = read_ssd(self.model_filepath)

        add_path(self.ssd.system)

        components = find_components(self.ssd.system)
        connectors = find_connectors(self.ssd.system)
        connections = get_connections(self.ssd.system)

        print("Components:")
        for component in components:
            print(f"  {component.name} {component.parent.name} {component.source}")

        print("Connectors:")
        if verbose:
            for connector in connectors:
                print(f"  {connector.parent.name}.{connector.name} {connector.kind}")
        else:
            for connector in self.ssd.system.connectors:
                print(f"  {connector.name} {connector.kind}")

        # resolve connections
        connections_reversed = {}

        for a, b in connections:
            connections_reversed[b] = a

        new_connections = []

        # trace connections back to the actual start connector
        for a, b in connections:

            while isinstance(a.parent, System) and a.parent.parent is not None:
                a = connections_reversed[a]

            new_connections.append((a, b))

        connections = new_connections

        if verbose:
            print("Connections:")
            for start_connector, end_connector in connections:
                print(f"  {start_connector.parent.name}.{start_connector.name} -> {end_connector.parent.name}.{end_connector.name}")

        # initialize the connectors
        for connector in connectors:
            connector.value = 0.0

        # set parameters
        for connector in self.ssd.system.connectors:
            if connector.kind == 'parameter' and connector.name in config_param_vals:
                if verbose:
                    print(f"setting {connector.parent.name}.{connector.name} to {config_param_vals[connector.name]}")
                connector.value = config_param_vals[connector.name]

        # instantiate the FMUs
        for component in components:
            # Get parameter set for this FMU
            # TODO: Is there a better way to use fmpy to handle initializing parameter values for the system?
            #       ssd.get_connections only handles inputs and outputs and it seems like simulate_ssp assumes the parameter set
            #       for the individual FMUs is already known instead of using connections from the system to calculate the parameters
            #       for the individual FMUs.
            parameter_set = ParameterSet()
            for start_connector, end_connector in self.get_system_parameter_connections(self.ssd.system):
                if end_connector.parent == component:
                    parameter = Parameter()
                    parameter.name = f"{component.name}.{end_connector.name}"
                    parameter.value = start_connector.value
                    parameter_set.parameters.append(parameter)
                    if verbose:
                        print(f"initializing {component.name} with {parameter.name} = {parameter.value}")

            instantiate_fmu(component, self.ssp_unzipdir, 0, stop_time=None, parameter_set=parameter_set)

        self.sim_time = 0

        if verbose:
            print("Initialized Connector Values:")
            for connector in connectors:
                print(f"  {connector.parent.name}.{connector.name} {connector.kind} {connector.value}")

    def run_step(self):
        components = find_components(self.ssd.system)
        connections = get_connections(self.ssd.system)

        # apply connections
        # TODO: Why doesn't simulate_ssp apply connections after initialization and after applying inputs?
        #       It seems like connections from system inputs should be applied before the step and connections to system outputs should be picked up after the step.
        # Are we correct to apply connections both before and after a step?
        # What about connections between FMUs? Should FMUs be executed in a particular order so that intermediate results can be passed from one to another without waiting for the next step?
        connections = get_connections(self.ssd.system)
        for start_connector, end_connector in connections:
            end_connector.value = start_connector.value

        # perform one step
        for component in components:
            do_step(component, self.sim_time, self.step_size)

        # apply connections
        for start_connector, end_connector in connections:
            end_connector.value = start_connector.value

        # advance the time
        self.sim_time += self.step_size

    def reset(self, config_param_vals: Dict[str, Any] = None):
        # TODO: Is there a fast and reliable way to reinitialize the whole SSP ensemble?
        # For now we'll just reload everything!

        # free the FMUs
        components = find_components(self.ssd.system)
        for component in components:
            free_fmu(component)

        self.initialize_model(config_param_vals)

    def apply_actions(self, b_action_vals: Dict[str, Any] = {}):
        for connector in self.ssd.system.connectors:
            if connector.kind == 'input' and connector.name in b_action_vals:
                connector.value = b_action_vals[connector.name]

    def get_state_vars(self):
        state = {}
        for connector in self.ssd.system.connectors:
            if connector.kind == 'output':
                state[connector.name] = connector.value
        return state

    def get_model_name(self):
        # TODO: Dynamically return model name from system
        return f"SSP Model"

    def get_system_parameter_connections(self, system, connectors=None):
        """ Create a list of (start_connector, end_connector) from all parameter connections in the system """

        if connectors is None:
            connectors = {}  # path -> object
            for connector in find_connectors(system):
                connectors[build_path(connector)] = connector

        cons = []

        # connections to the outside
        for connector in system.connectors:

            if connector.kind == 'parameter':

                # find the connection
                for connection in system.connections:
                    if connection.endElement is None and connection.endConnector == connector.name:
                        start_p = build_path(system) + '.' + connection.startElement + '.' + connection.startConnector
                        end_p = build_path(connector)
                        break
                    elif connection.startElement is None and connection.startConnector == connector.name:
                        start_p = build_path(connector)
                        end_p = build_path(system) + '.' + connection.endElement + '.' + connection.endConnector
                        break

                cons.append((connectors[start_p], connectors[end_p]))

        # TODO: Should this handle internal connections or child system connections? Compare with ssd.get_connections.

        return cons
