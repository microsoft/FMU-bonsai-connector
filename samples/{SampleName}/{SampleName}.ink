# This file must contain sample Inkling for a Bonsai brain that can be trained with the {SampleName} simulator.
#
# The purpose is to demonstrate that the simulator sample's states, actions, and configuration parameters
# work correctly and that training with the {SimPlatform} connector works correctly.
#
# It is not necessary for the brain to actually learn something realistic and useful, although the sample will be more interesting
# and compelling if does!

inkling "2.0"

using Math
using Goal

# Type that represents the per-iteration state returned by simulator
type SimState {
    ...