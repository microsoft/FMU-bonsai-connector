#!/usr/bin/env python
"""
Script for testing the FMU connector with a particular FMU file.

Goals:
- Makes it easy to run the connector with an FMU using the recommended workflow.
- Should run in a way that is as similar as possible to the way the final connector will function when running inside a container.
- Should log the steps that it is performing and show the Docker and Bonsai CLI commands that are being run.
"""

import os
import shutil
import pathlib
import subprocess

log_command_output: bool = False

def run_command(command: str, return_json: bool=False, errors_expected: bool=False):
    print(f"  > {command}")
    process = subprocess.run(command, capture_output=return_json, text=True)
    if log_command_output:
        print(f"""
returncode: {process.returncode}
stderr: {process.stderr}
stdout: {process.stdout}
""".strip())
    if process.returncode != 0:
        if not errors_expected:
            print(process.stderr)
        return None
    if not return_json:
        return None
    result_json = json.loads(process.stdout)
    return result_json

def delete_if_exists(path: str, is_directory: bool = False):
    if os.path.exists(path):
        if is_directory:
            shutil.rmtree(path)
        else:
            os.remove(path)
        print(f"  deleted {path}")

def copy_file(source, destination):
    shutil.copyfile(source, destination)
    print(f"  copied {source} -> {destination}")

def main(mode: str, fmu_path: str):
    if not os.path.exists(fmu_path):
        print(f"test-fmu.py: error: File {fmu_path} not found.")
    if not "SIM_WORKSPACE" in os.environ:
        print("test-fmu.py: error: SIM_WORKSPACE environment variable must be set to your Bonsai workspace ID.")
    if not "SIM_ACCESS_KEY" in os.environ:
        print("test-fmu.py: error: SIM_ACCESS_KEY environment variable must be set to your Bonsai workspace access key.")

    fmu_connector_root_directory = pathlib.Path(__file__).resolve().parent.parent

    print("* Cleaning up previous temporary sample files")
    delete_if_exists(f"{fmu_connector_root_directory}\\generic\\generic.fmu")
    delete_if_exists(f"{fmu_connector_root_directory}\\generic\\generic_conf.yaml")
    delete_if_exists(f"{fmu_connector_root_directory}\\generic\\generic_unzipped", is_directory = True)
    print()

    print("* Copying new sample files")
    copy_file(fmu_path, f"{fmu_connector_root_directory}\\generic\\generic.fmu")
    print()

    print("* Launching local simulator")
    run_command(f"cmd /c start python {fmu_connector_root_directory}\\generic\\main.py")

if __name__ == "__main__":

    import argparse

    epilog_text = """
Examples:
 test-fmu -mode local vanDerPol.fmu
    Run vanDerPol.fmu locally as an unmanaged sim.
 test-fmu -mode local-container Integrator.fmu
    Run Integrator.fmu locally in a Docker container as an unmanaged sim.
 test-fmu -mode local-container vanDerPol.fmu
    Create a managed sim in your Bonsai workspace for running vanDerPol.fmu.
""".strip()

    parser = argparse.ArgumentParser(
        description="Test the FMU connector with an FMU file.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog_text)

    mode_help = """
Testing mode. Choices are:
local: Run an unmanaged simulator on your local machine.
    Best for testing and debugging the FMU connector Python code.
local-container: Build the connector containers and run them as an unmanaged simulator
    inside Docker on your local machine. Best for testing and troubleshooting how the
    FMU connector works inside Docker.
managed: Build the connector containers and add them as a managed simulator in your
    Bonsai workspace. Best for testing and troubleshooting how the FMU connector
    works when running at scale inside the Bonsai service.
""".strip()

    parser.add_argument(
        "--mode",
        choices=["local", "local-container", "managed"],
        required=True,
        help=mode_help,
    )

    parser.add_argument(
        "fmu_path",
        type=str)

    args = parser.parse_args()
    main(args.mode, args.fmu_path)
