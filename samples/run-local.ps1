Param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]
    $FmuPath
)

if ("$Env:SIM_WORKSPACE" -eq "") { Write-Output "You must set the SIM_WORKSPACE environment variable to use this script."; return }
if ("$Env:SIM_ACCESS_KEY" -eq "") { Write-Output "You must set the SIM_ACCESS_KEY environment variable to use this script."; return }

$FmuConnectorRoot = (get-item $PSScriptRoot).parent.FullName

Write-Output "* Copying $FmuPath to $FmuConnectorRoot\generic\generic.fmu"
remove-item "C:\s\Bonsai\FMU-bonsai-connector\generic\generic*" -Recurse # delete previously-existing generic.fmu file and the associated config and unzipped contents
copy $FmuPath $FmuConnectorRoot\generic\generic.fmu

Write-Output "* Launching local simulator"
python $FmuConnectorRoot/generic/main.py
