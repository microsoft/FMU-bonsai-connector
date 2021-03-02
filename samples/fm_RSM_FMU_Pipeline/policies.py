"""
Fixed policies to test our sim integration with. These are intended to take
Brain states and return Brain actions.
"""

import random
from typing import Dict


def random_policy(state: Dict = None):
    """
    Ignore the state, move randomly.
    """
    action = { "v1_in_inlet_pressure": random.randint(50000, 100000),
               "v2_in_pipe_diameter":  float(random.randint(2, 15))/10 }
    return action


POLICIES = {"random": random_policy}

