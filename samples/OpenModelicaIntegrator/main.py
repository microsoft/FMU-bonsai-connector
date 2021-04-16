#!/usr/bin/env python
"""
Microsoft-Bonsai-API integration with House Energy Simulator
"""

# [TODO] Review package import... not clean at the moment
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "//..//..//FMU_Connector")

import pathlib
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

# TODO_PER_SIM 10: Turn to False after model in/out config vars have been verified
# - You can turn this off once you are satisfied with the config saved to "sim\{model_name}_conf.yaml"
FIRST_TIME_RUNNING = True

# TODO_PER_SIM 1: read FMI version from modelDescription.xml
# - you can manually unzip the folder to check, or run with FMI_VERSIOn=2.0, and get it unpacked
# ("1.0", "2.0", "3.0")
FMI_VERSION = "2.0"

# TODO_PER_SIM 2: Set to True when dealing with a steady state simulator (no time evolution involved)
STEADY_STATE_SIM = False

# TODO_PER_SIM 3: define start, stop, and step size
# - stop and step size values are overwritten for steady state sims
START_TIME = 0.0
STOP_TIME = 2.0
STEP_SIZE = 0.1
# if steady-state sim, default to {STOP_TIME = 1.0} & {STEP_SIZE = 0.1}
if STEADY_STATE_SIM:
    STOP_TIME = 1.0
    STEP_SIZE = 0.1

# TODO_PER_SIM 4: define default config file (if None provided by brain)
DEFAULT_CONFIG = {}

class FMUSimulatorSession:
    # TODO_PER_SIM 5: Set-up model filepath (modeldir) & sim name (env_name) variables
    def __init__(
        self,
        modeldir: str = "sim\\Integrator.fmu",
        env_name: str = "OpenModelicaIntegrator",
        log_file: Union[str, None] = None,
    ):
        """Template for simulating FMU models with FMUConnector

        Parameters
        ----------
        modeldir: str, optional
            relative filepath to your FMU sim (e.g: "sim\\Integrator.fmu", if in sim subfolder)
        env_name: str, optional
            name of simulator environment, registered by SimulatorInterface
            note, this will be your sim name in preview.bons.ai
        """

        self.modeldir = modeldir
        self.model_full_path = os.path.join(dir_path, self.modeldir)
        self.env_name = env_name
        print("Using simulator file from: ", self.model_full_path)

        self.default_config = DEFAULT_CONFIG

        # Validate and instance FMU model
        self.simulator = FMUConnector(model_filepath = self.model_full_path,
                                      fmi_version = FMI_VERSION,
                                      start_time = START_TIME,
                                      stop_time = STOP_TIME,
                                      step_size = STEP_SIZE,
                                      user_validation = FIRST_TIME_RUNNING)

        # initialize model - required!
        self.simulator.initialize_model()

        self._reset()
        self.terminal = False
        if not log_file:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file = current_time + "_" + env_name + "_log.csv"
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

        # TODO_PER_SIM 6: (optional) Modify states to be sent to Bonsai
        # - currently, all states are sent to Bonsai: config_params, states (sim outputs), and actions (sim inputs)
        return self.simulator.get_all_vars()


    def _reset(self, config: dict = None):
        """Helper function for resetting a simulator environment
           Runs with config provided by Bonsai (if given), uses default config otherwise

        Parameters
        ----------
        config : dict, optional
            [description], by default None
        """

        if config:
            if len(config.items()) > 0:
                self.sim_config = config
            else:
                self.sim_config = self.default_config
        else:
            self.sim_config = self.default_config

        self.simulator.reset(self.sim_config)


    def episode_start(self, config: Dict[str, Any] = None):
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
        
        # TODO_PER_SIM 7: Add any action transformation required (from Bonsai to sim)
        # Apply actions
        self.simulator.apply_actions(action)

        # Run sim one step forward
        # - Stepping is performed only on sims that evolve over time (STEADY_STATE_SIM == False)
        if not STEADY_STATE_SIM:
            self.simulator.run_step()


    def halted(self) -> bool:
        """Should return True if the simulator cannot continue"""
        # TODO_PER_SIM 8: Define any halt conditions
        return self.terminal

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
        config = add_prefixes(self.default_config, "config")
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

    if not all([env_file_exists, workspace]):
        workspace = input("Please enter your workspace id: ")
        set_key(".env", "SIM_WORKSPACE", workspace)
    if not all([env_file_exists, access_key]):
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

    sim = FMUSimulatorSession(log_file="OpenModelicaIntegrator.csv") 
    for episode in range(num_episodes):
        iteration = 0
        terminal = False
        obs = sim.episode_start()
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


def main(config_setup: bool = False):
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
    sim = FMUSimulatorSession()

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # # Load json file as simulator integration config type file
    # with open("interface.json") as file:
    #     interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
        name=sim.env_name,
        timeout=60,
        simulator_context=config_client.simulator_context,
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
                print("Simulator Session unregistered by platform because '{}', Registering again!".format(event.unregister.details))
                client.session.delete(
                    workspace_name=config_client.workspace,
                    session_id=registered_session.session_id,
                )
                print("Unregistered simulator.")
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

    args = parser.parse_args()

    if args.test_local:
        test_random_policy(
            num_episodes=1000, log_iterations=args.log_iterations
        )
    else:
        main(config_setup=args.config_setup)

