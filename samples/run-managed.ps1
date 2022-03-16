Param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]
    $FmuPath
)

if ("$Env:SIM_WORKSPACE" -eq "") { Write-Output "You must set the SIM_WORKSPACE environment variable to use this script."; return }
if ("$Env:SIM_ACCESS_KEY" -eq "") { Write-Output "You must set the SIM_ACCESS_KEY environment variable to use this script."; return }
if ("$Env:SIM_ACR_PATH" -eq "") { Write-Output "You must set the SIM_ACR_PATH environment variable to use this script."; return }

$FmuConnectorRoot = (get-item $PSScriptRoot).parent.FullName

Write-Output "* Clearing previous FMU files"
remove-item $FmuConnectorRoot\Sim.zip -ErrorAction Ignore
remove-item "$FmuConnectorRoot\generic\generic*" -Recurse

Write-Output "* Building base image"
#docker image rm fmu_base:latest
docker build -t fmu_base:latest -f $FmuConnectorRoot\Dockerfile-windows_FMU_BASE $FmuConnectorRoot

Write-Output "* Zipping $FmuPath to $FmuConnectorRoot\sim.zip"
Compress-Archive -LiteralPath $FmuPath -DestinationPath $FmuConnectorRoot\Sim.zip

Write-Output "* Building runtime image"
#docker image rm fmu_runtime:latest
docker build -t fmu_runtime:latest -f $FmuConnectorRoot\Dockerfile-windows_FMU_RUNTIME $FmuConnectorRoot

Write-Output "* Pushing to ACR"
az acr login --name $Env:SIM_ACR_PATH
docker tag fmu_runtime:latest $Env:SIM_ACR_PATH/fmu_runtime:latest
docker push $Env:SIM_ACR_PATH/fmu_runtime:latest

Write-Output "* Creating Bonsai simulator"
bonsai simulator package container create -n fmu_runtime -u $Env:SIM_ACR_PATH/fmu_runtime:latest --max-instance-count 25 -r 1 -m 1 -p Windows

Write-Output "* Done"
