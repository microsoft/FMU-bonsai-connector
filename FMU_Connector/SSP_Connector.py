from typing import Any, Dict, List, Union

class SSPConnector:
    def __init__(
        self,
        model_filepath: str
    ):
        self.error_occurred = False
        self.sim_time = 0

    def initialize_model(self, config_param_vals = None):
        pass

    def run_step(self):
        pass

    def reset(self, config_param_vals: Dict[str, Any] = None):
        pass

    def apply_actions(self, b_action_vals: Dict[str, Any] = {}):
        pass

    def get_state_vars(self):
        return {}

    def get_model_name(self):
        return f"SSP Model"
