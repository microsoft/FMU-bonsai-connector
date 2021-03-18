###

# MSFT Bonsai 
# Copyright 2021 Microsoft
# This code is licensed under MIT license (see LICENSE for details)

# FMU Integration - Flomaster Pipeline
# This introductory sample demonstrates how to integrate any sim 
# released under the FMI standard.
# See more at: "https://fmi-standard.org/"

###

inkling "2.0"

using Math
using Number
using Goal

# Number of iterations - Note, this is a steady-state sim (time does not pass by)
const num_iterations = 20

# Target flow
const target_flow = 0.00005

# State received from the simulator after each iteration
type SimState {
    # Fluid velocity
    o1_out_fluid_velocity: number,
    # Out flow rate
    o2_out_flow_rate: number,
    # Pressure drop
    o3_out_pressure_drop: number,
}

# Action provided as output by policy and sent as
# input to the simulator
type SimAction {
    # Pressure on pipe
    v1_in_inlet_pressure: number<50000 .. 100000>,
    # Pipe diameter
    v2_in_pipe_diameter: number<0.2 .. 1.5>,
}

# Per-episode configuration that can be sent to the simulator.
# All iterations within an episode will use the same configuration.
type SimConfig {
    # Oscillation parameter
    none: 0,
}

# Define a concept graph with a single concept
graph (input: SimState) {
    concept ReachTargetPipeflow(input): SimAction {
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

            # The objective of training is to match the fluid velocity to the target value.
            goal (State: SimState) {
                minimize `ErrorToTargetFlow`: 
                    Math.Abs(State.o1_out_fluid_velocity - target_flow) in Goal.RangeBelow(0.000005)
            }
        }
    }
}
