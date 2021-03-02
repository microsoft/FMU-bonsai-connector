# {SimPlatform} connector

***Replace {SimPlatform} with the name of your simulation platform and fill out this template as described in the markdown files.***

A connector for using {SimPlatform} with [Microsoft Project Bonsai](https://azure.microsoft.com/en-us/services/project-bonsai/).

## Installation

> This section should list steps for installing components that users will need, such as:
> * {SimPlatform} applications, tools, or SDKs
> * The connector itself
> * Any other dependencies required by the connector

## Usage: Running a local simulator

> Assume that a user has already created a simulation using {SimPlatform}. Feel free to include a link to {SimPlatform}'s documentation if you think it would be helpful, but it isn't necessary to document how to use {SimPlatform} itself.
>
> This section should list steps for using the connector to run a {SimPlatform} simulation with the Bonsai service as a local simulator, such as:
> * Required or recommended settings that must be made in {SimPlatform} when users create simulations.
> * How the simulation's states, actions, and initial configuration should be set up in {SimPlatform}.
> * How to execute the simulation as a local Bonsai simulator. For example, this could include an example command-line argument for doing so.
> * How to identify if your local simulator is running correctly. For example, something like: If the simulation is running successfully, command line output should show "Sim successfully registered" and the Bonsai workspace should show the {SimPlatform} simulator name under the Simulators section, listed as Unmanaged.
>
> Optional: Does the connector for {SimPlatform} allow an integrated way of launching a local simulator, debugging a local simulator, or visualizing a local simulator as it executes via a user interface inside {SimPlatform}? Such capabilities can be described here.

## Usage: Scaling your simulator

> This section should list steps for running multiple simulator instances to scale Bonsai training.
>
> Typically this is done by adding a simulator container to your Bonsai workspace. In that case, this section will include:
> * Command line arguments for building a container with the {SimPlatform} connector and the user's simulation.
> * A link to the documentation topic [Add a training simulator to your Bonsai workspace](https://docs.microsoft.com/en-us/bonsai/guides/add-simulator?tabs=add-cli%2Ctrain-inkling&pivots=sim-platform-other) for information about how to upload the container, add it to Bonsai, and scale the simulator.
>
> It is less desirable, but if it is the case that {SimPlatform} cannot be run inside a scalable container then an alternate means of scaling simulator instances such as [bonsai-batch](https://github.com/microsoft/bonsai-batch) can be documented here.
>
> Optional: Does the connector for {SimPlatform} allow an integrated way of uploading a simulator to the Bonsai service or scaling the simulator instances for training via a user interface inside {SimPlatform}? Such capabilities can be described here.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
