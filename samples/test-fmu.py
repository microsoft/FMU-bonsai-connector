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
from zipfile import ZipFile

log_command_output: bool = False

def print_highlighted(message: str):
    # Send special escape sequences that print text in the color blue on most terminals.
    print(f"\033[94m{message}\033[0m")

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
            if process.stderr != None:
                print(process.stderr)
            sys.exit()
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

def main(mode: str, fmu_path: str):
    if not os.path.exists(fmu_path):
        print(f"test-fmu.py: error: File {fmu_path} not found.")
    if not "SIM_WORKSPACE" in os.environ:
        print("test-fmu.py: error: SIM_WORKSPACE environment variable must be set to your Bonsai workspace ID.")
    if not "SIM_ACCESS_KEY" in os.environ:
        print("test-fmu.py: error: SIM_ACCESS_KEY environment variable must be set to your Bonsai workspace access key.")

    # Determine the FMU connector root directory by its relative path from this script file.
    root_dir = pathlib.Path(__file__).resolve().parent.parent

    print_highlighted("Cleaning up previous temporary sample files")
    delete_if_exists(f"{root_dir}\\sim.zip")
    delete_if_exists(f"{root_dir}\\generic\\generic.fmu")
    delete_if_exists(f"{root_dir}\\generic\\generic_conf.yaml")
    delete_if_exists(f"{root_dir}\\generic\\generic_unzipped", is_directory = True)
    print()

    if mode == "local":
        print_highlighted("Copying new sample files")
        generic_fmu_path = f"{root_dir}\\generic\\generic.fmu"
        shutil.copyfile(fmu_path, generic_fmu_path)
        print(f"  copied {fmu_path} -> {generic_fmu_path}")
        print()
        print_highlighted("Launching local simulator")
        run_command(f"cmd /c start python {root_dir}\\generic\\main.py")
    elif mode == "local-container":
        print_highlighted("Building base image")
        run_command(f"docker build -t fmu_base:latest -f {root_dir}\\Dockerfile-windows_FMU_BASE {root_dir}")
        print()
        print(f"* Zipping {fmu_path}")
        zip_path = f"{root_dir}\Sim.zip"
        with ZipFile(zip_path, 'w') as zipfile:
            zipfile.write(fmu_path, arcname=pathlib.Path(fmu_path).name)
        print(f"  zipped {fmu_path} -> {zip_path}")
        print()
        print_highlighted("Building runtime image")
        run_command(f"docker build -t fmu_runtime:latest -f {root_dir}\\Dockerfile-windows_FMU_RUNTIME {root_dir}")
        print_highlighted("Launching local container")
        run_command(f"cmd /c start docker run -it --rm -e SIM_ACCESS_KEY=%SIM_ACCESS_KEY% -e SIM_WORKSPACE=%SIM_WORKSPACE% fmu_runtime:latest")


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
