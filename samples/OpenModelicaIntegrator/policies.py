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
    action = { "u": random.randint(0, 10) - 5 }
    return action


POLICIES = {"random": random_policy}

