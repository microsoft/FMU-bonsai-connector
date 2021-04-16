###

# MSFT Bonsai 
# Copyright 2021 Microsoft
# This code is licensed under MIT license (see LICENSE for details)

# FMU Integration - OpenModelica Integrator
# This introductory sample demonstrates how to use an OpenModelica model with Bonsai
# using the FMI standard.
# See more at: "https://fmi-standard.org/"

###

inkling "2.0"

using Math
using Number
using Goal

# Number of iterations
const num_iterations = 20

# Target value
const target = 12

# State received from the simulator after each iteration
type SimState {
    x: number,
}

# Action provided as output by policy and sent as input to the simulator
type SimAction {
    u: number<-5.0 .. 5.0>,
}

# Per-episode configuration that can be sent to the simulator.
# All iterations within an episode will use the same configuration.
type SimConfig {
    none: 0,
}

# Define a concept graph with a single concept
graph (input: SimState) {
    concept ReachTarget(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator that
            #  - can be configured for each episode using fields defined in SimConfig,
            #  - accepts per-iteration actions defined in SimAction, and
            #  - outputs states with the fields defined in SimState.
            source simulator Simulator(Action: SimAction, Config: SimConfig): SimState {
            }

            training {
                # Limit episodes to num_iterations instead of the default 1000.
                EpisodeIterationLimit: num_iterations,
                NoProgressIterationLimit: 750000
            }
             
            algorithm {
                Algorithm: "SAC",
            }

            # The objective of training is to match the value of x to the target value.
            goal (State: SimState) {
                drive `Two`: 
                    Math.Abs(State.x - target) in Goal.RangeBelow(0.1)
            }
        }
    }
}
