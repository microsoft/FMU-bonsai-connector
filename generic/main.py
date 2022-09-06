#!/usr/bin/env python
"""
Microsoft-Bonsai-API integration with House Energy Simulator
"""

# [TODO] Review package import... not clean at the moment
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "//..//..//FMU_Connector")
sys.path.insert(0, dir_path + "//..//FMU_Connector")

import pathlib
import json
import time
import datetime
from distutils.util import strtobool
from typing import Any, Dict, List, Union

from dotenv import load_dotenv, set_key
from FMU_Connector import FMUConnector
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface,
    SimulatorState,
)


from policies import random_policy

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = "logs"

# TODO_PER_SIM 1: read FMI version from modelDescription.xml
# - you can manually unzip the folder to check, or run with FMI_VERSIOn=2.0, and get it unpacked
# ("1.0", "2.0", "3.0")
FMI_VERSION = "2.0"

class FMUSimulatorSession:
    # TODO_PER_SIM 5: Set-up model filepath (modeldir) & sim name (env_name) variables
    def __init__(
        self,
        fmi_logging: bool = False,
        modeldir: str = "generic.fmu",
        log_file: Union[str, None] = None,
    ):
        """Template for simulating FMU models with FMUConnector

        Parameters
        ----------
        modeldir: str, optional
            relative filepath to your FMU sim (e.g: "sim\\vanDerPol.fmu", if in sim subfolder)
        env_name: str, optional
            name of simulator environment, registered by SimulatorInterface
            note, this will be your sim name in preview.bons.ai
        """

        self.modeldir = modeldir
        self.model_full_path = os.path.join(dir_path, self.modeldir)
        print("Using simulator file from: ", self.model_full_path)

        # Validate and instance FMU model
        self.simulator = FMUConnector(model_filepath = self.model_full_path,
                                      fmi_version = FMI_VERSION,
                                      user_validation = False,
                                      fmi_logging = fmi_logging)
        self.env_name = f"{self.simulator.model_description.modelName} FMU"

        # initialize model - required!
        self.simulator.initialize_model()

        if not log_file:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file = current_time + "_" + self.env_name + "_log.csv"
            log_file = os.path.join(log_path, log_file)
            logs_directory = pathlib.Path(log_file).parent.absolute()
            if not pathlib.Path(logs_directory).exists():
                print(
                    "Directory does not exist at {0}, creating now...".format(
                        str(logs_directory)
                    )
                )
                logs_directory.mkdir(parents=True, exist_ok=True)
        self.log_file = os.path.join(log_path, log_file)

    def get_state(self) -> Dict[str, float]:
        """ Called to retreive the current state of the simulator. """
        return self.simulator.get_state_vars()


    def _reset(self, config: dict):
        """Helper function for resetting a simulator environment
           Runs with config provided by Bonsai (if given), uses default config otherwise

        Parameters
        ----------
        config : dict, optional
            [description], by default None
        """

        self.sim_config = config
        self.simulator.reset(self.sim_config)


    def episode_start(self, config: Dict[str, Any]):
        """Method invoked at the start of each episode to reset the sim with a given episode configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            SimConfig parameters for the current episode defined in Inkling
        """

        self._reset(config)


    def episode_step(self, action: Dict[str, Any]):
        """Called for each step of the episode 

        Parameters
        ----------
        action : Dict[str, Any]
            BrainAction chosen from the Bonsai Service, prediction or exploration
        """

        sim_action = action

        # TODO_PER_SIM 7: Add any action transformation required (from Bonsai to sim)
        # We don't currently support a general-purpose custom logic mechanism for action transformations.
        # Custom logic for the van der Pol oscillator sample to perform an action transformation
        # --> x0 += x0_adjust
        if self.simulator.model_description.guid == '{8c4e810f-3da3-4a00-8276-176fa3c9f000}':
            if 'x0_adjust' in action:
                x0_adjust = action['x0_adjust']
                sim_action_val = self.simulator.get_states(['x0'])['x0']
                sim_action = {'x0': sim_action_val + x0_adjust}

        self.simulator.apply_actions(sim_action)

        # Run sim one step forward
        self.simulator.run_step()

    def halted(self) -> bool:
        """Should return True if the simulator cannot continue"""
        return self.simulator.error_occurred

    def random_policy(self, state: Dict = None) -> Dict:
        # TODO_PER_SIM 9: Update the random policy to be used for the example on policies.py
        return random_policy()

    def log_iterations(self, state, action, episode: int = 0, iteration: int = 1):
        """Log iterations during training to a CSV.

        Parameters
        ----------
        state : Dict
        action : Dict
        episode : int, optional
        iteration : int, optional
        """

        import pandas as pd

        def add_prefixes(d, prefix: str):
            return {f"{prefix}_{k}": v for k, v in d.items()}

        state = add_prefixes(state, "state")
        action = add_prefixes(action, "action")
        config = add_prefixes(self.sim_config, "config")
        data = {**state, **action, **config}
        data["episode"] = episode
        data["iteration"] = iteration
        log_df = pd.DataFrame(data, index=[0])

        if os.path.exists(self.log_file):
            log_df.to_csv(
                path_or_buf=self.log_file, mode="a", header=False, index=False
            )
        else:
            log_df.to_csv(path_or_buf=self.log_file, mode="w", header=True, index=False)


def env_setup():
    """Helper function to setup connection with Project Bonsai

    Returns
    -------
    Tuple
        workspace, and access_key
    """

    load_dotenv(verbose=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    env_file_exists = os.path.exists(".env")
    if not env_file_exists:
        open(".env", "a").close()

    if not env_file_exists and not workspace:
        workspace = input("Please enter your workspace id: ")
        set_key(".env", "SIM_WORKSPACE", workspace)
    if not env_file_exists and not access_key:
        access_key = input("Please enter your access key: ")
        set_key(".env", "SIM_ACCESS_KEY", access_key)

    load_dotenv(verbose=True, override=True)
    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    return workspace, access_key


def test_random_policy(
    num_episodes: int = 10,
    log_iterations: bool = False,
    max_iterations: int = 288,
):
    """Test a policy using random actions over a fixed number of episodes

    Parameters
    ----------
    num_episodes : int, optional
        number of iterations to run, by default 10
    """

    # TODO_PER_SIM 4: define default config file for test_random_policy
    DEFAULT_CONFIG = {"mu": 1.5,}

    sim = FMUSimulatorSession(log_file="VanDerPol_Oscillations.csv") 
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        obs = sim.episode_start(DEFAULT_CONFIG)
        while not terminal:
            action = sim.random_policy()
            sim.episode_step(action)
            sim_state = sim.get_state()
            if log_iterations:
                sim.log_iterations(
                    state=sim_state, action=action, episode=episode, iteration=iteration
                )
            print(f"Running iteration #{iteration} for episode #{episode}")
            print(f"Observations: {sim_state}")
            iteration += 1
            terminal = iteration > max_iterations


def main(config_setup: bool, fmi_logging: bool):
    """Main entrypoint for running simulator connections

    Parameters
    ----------
    config_setup : bool, optional
        apply config setup using .env file, by default False
    """

    # workspace environment variables
    if config_setup:
        env_setup()
        load_dotenv(verbose=True, override=True)

    # Grab standardized way to interact with sim API
    sim = FMUSimulatorSession(fmi_logging=fmi_logging)

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # # Load json file as simulator integration config type file
    with open("interface.json") as file:
        interface = json.load(file)

    # If the user-overrideable transform contains a timeout variable, override the default timeout value.
    # This is not an ideal solution, but we don't currently have a better way to configure such as setting.
    timeout = 60
    if hasattr(sim.simulator.transform, "timeout"):
        timeout = sim.simulator.transform.timeout

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=timeout,
        simulator_context=config_client.simulator_context,
        description=interface['description']
    )
    registered_session = client.session.create(
        workspace_name=config_client.workspace, body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=sim.halted(),
            )
            event = client.session.advance(
                workspace_name=config_client.workspace,
                session_id=registered_session.session_id,
                body=sim_state,
            )
            sequence_id = event.sequence_id
            print(f'[{time.strftime("%H:%M:%S")}] Last Event: {event.type}, Sim Time: {sim.simulator.sim_time:.3f}')

            # Event loop
            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
                print("Idling...")
            elif event.type == "EpisodeStart":
                sim.episode_start(event.episode_start.config)
            elif event.type == "EpisodeStep":
                sim.episode_step(event.episode_step.action)
            elif event.type == "EpisodeFinish":
                print("Episode Finishing...")
            elif event.type == "Unregister":
                print("Simulator Session unregistered by platform because '{}'.".format(event.unregister.details))
                client.session.delete(
                    workspace_name=config_client.workspace,
                    session_id=registered_session.session_id,
                )
                print("Unregistered simulator. Exiting.")
                return
            else:
                pass
    except KeyboardInterrupt:
        # Gracefully unregister with keyboard interrupt
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator.")
    except Exception as err:
        # Gracefully unregister for any other exceptions
        client.session.delete(
            workspace_name=config_client.workspace,
            session_id=registered_session.session_id,
        )
        print("Unregistered simulator because: {}".format(err))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")
    parser.add_argument(
        "--log-iterations",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Log iterations during training",
    )
    parser.add_argument(
        "--config-setup",
        type=lambda x: bool(strtobool(x)),
        default=True,
        help="Use a local environment file to setup access keys and workspace ids",
    )
    parser.add_argument(
        "--test-local",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Run simulator locally without connecting to platform",
    )
    parser.add_argument(
        "--fmi-logging",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Print each FMU API call to the console output",
    )

    args = parser.parse_args()

    if args.test_local:
        test_random_policy(
            num_episodes=1000, log_iterations=args.log_iterations
        )
    else:
        main(config_setup=args.config_setup, fmi_logging=args.fmi_logging)

