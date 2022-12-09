inkling "2.0"
using Goal
using Math

type SimConfig {
    outter_initial_value: number,
}

type SimState {
    outter_value: number
}

type Action {
    outter_addend: number<-10 .. 10>
}

graph (input: SimState): Action {
    concept Concept(input): Action {
        curriculum {
            source simulator (Action: Action, Config: SimConfig): SimState {
            }

            training {
                EpisodeIterationLimit: 10
            }

            goal (state: SimState) {
                reach Goal:
                    state.outter_value
                    in Goal.Range(49.9, 50.1)
            }

            lesson `learn 1` {
                scenario {
                    outter_initial_value: number<0 .. 100>,
                }
            }
        }
    }
}
