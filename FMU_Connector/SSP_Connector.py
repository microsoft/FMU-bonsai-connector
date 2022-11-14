from fmpy import extract
from fmpy.ssp.ssd import System, read_ssd, get_connections, find_connectors, find_components
from fmpy.ssp.simulation import add_path, instantiate_fmu, do_step, free_fmu
from typing import Any, Dict, List, Union

class SSPConnector:
    def __init__(
        self,
        model_filepath: str
    ):
        self.model_filepath = model_filepath

        # extract the SSP
        self.ssp_unzipdir = extract(self.model_filepath)


    def initialize_model(self, config_param_vals = None):
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
        for connector in connectors:
            print(f"  {connector.name} {connector.kind} {connector.parent.name}")

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

        # initialize the connectors
        for connector in connectors:
            connector.value = 0.0

        # instantiate the FMUs
        for component in components:
            instantiate_fmu(component, self.ssp_unzipdir, 0, stop_time=None, parameter_set=None)

        self.sim_time = 0

    def run_step(self):
        components = find_components(self.ssd.system)
        connections = get_connections(self.ssd.system)
        
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

        self.initialize_model()

    def apply_actions(self, b_action_vals: Dict[str, Any] = {}):
        for connector in self.ssd.system.connectors:
            if connector.kind == 'input' and connector.name in b_action_vals:
                connector.value = b_action_vals[connector.name]

        # Apply actions to child systems.
        # TODO: This may be unnecessary. The DC-Motor example doesn't have input on the main system. Once we create a test case with input on the main system, can we remove this?
        connectors = find_connectors(self.ssd.system)
        for connector in connectors:
            if connector.kind == 'input' and connector.name in b_action_vals:
                connector.value = b_action_vals[connector.name]


    def get_state_vars(self):
        # TODO: Is this getting state on all connectors including children with duplicate names? Should we just do self.ssd.system.connectors?
        state = {}
        connectors = find_connectors(self.ssd.system)
        for connector in connectors:
            if connector.kind == 'output':
                state[connector.name] = connector.value
        return state

    def get_model_name(self):
        # TODO: Dynamically return model name from system
        return f"SSP Model"
