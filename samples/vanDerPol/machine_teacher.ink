###

# MSFT Bonsai 
# Copyright 2021 Microsoft
# This code is licensed under MIT license (see LICENSE for details)

# FMU Integration - VanDerPol Oscillations
# This introductory sample demonstrates how to integrate any sim 
# released under the FMI standard.
# See more at: "https://fmi-standard.org/"

###

inkling "2.0"

using Math
using Number
using Goal

# Simulation Step
const step_size = 0.1
# Simulation Start Time
const start_time = 0.0
# Simulation Stop Time
const stop_time = 20.0

# Number of iterations
const num_iterations = (stop_time-start_time)/step_size

# State received from the simulator after each iteration
type SimState {
    # x0: First state
    x0: number,
    # x1: Second state
    x1: number,
    
    # First derivative of x0
    derx0: number,
    # First derivative of x1
    derx1: number,
}


# State which is used to train the brain
# - set of states that the brain will have access to when deployed -
type ObservableState {
    # x0: First state
    x0: number,
    # x1: Second state
    x1: number,
}

# Action provided as output by policy and sent as
# input to the simulator
type SimAction {
    # Delta to be applied to initial state
    x0_adjust: number<-0.2 .. 0.2>
}

# Per-episode configuration that can be sent to the simulator.
# All iterations within an episode will use the same configuration.
type SimConfig {
    # Oscillation parameter
    mu: number<0.5 .. 4>,
}

# Define a concept graph with a single concept
graph (input: ObservableState) {
    concept ReduceOscillation(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator that
            #  - can be configured for each episode using fields defined in SimConfig,
            #  - accepts per-iteration actions defined in SimAction, and
            #  - outputs states with the fields defined in SimState.
            source simulator Simulator(Action: SimAction, Config: SimConfig): SimState {
            }

            training {
                # Limit episodes to 90 iterations instead of the default 1000.
                EpisodeIterationLimit: num_iterations,
                NoProgressIterationLimit: 750000
            }
             
            algorithm {
                Algorithm: "SAC",
            }

            # The objective of training is expressed as 3 goals
            # (1) drive concentration close to reference
            # (2) avoid temperature going beyond limit
            # (3) avoid temperature changing too fast (accomplished with max action value)
            goal (State: SimState) {
                minimize `Oscillation`: 
                    Math.Abs(State.x0)+Math.Abs(State.x1) in Goal.RangeBelow(1)
            }

            lesson `Follow Planned Concentration` {
                # Specify the configuration parameters that should be varied
                # from one episode to the next during this lesson.
                scenario {
                    # Oscillation parameter
                    mu: number<0.5 .. 4>
                }
            }
        }
    }
}
