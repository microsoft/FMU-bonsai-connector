@REM Use this bat file to build and push the fmu base container, then contact Service to upload and get configs correct

@REM %SIM_ACR_PATH% must be set, get this from the Azure Portal in your Managed Resource Group (ex. xxxx.azurecr.io)
docker build -t fmu_base:latest -f Dockerfile-windows_FMU_BASE .

docker tag fmu_base:latest %SIM_ACR_PATH%/fmu_base:latest

@REM if errors check subscription is correct default, if not use this instead
@REM az acr login --subscription <SUBSCRIPTION> --name %SIM_ACR_PATH%
call az acr login --name %SIM_ACR_PATH%

docker push %SIM_ACR_PATH%/fmu_base:latest

@ECHO Please ensure the last update date in your ACR (at the image level) has been updated to current date
@ECHO Provide Service with: 
@ECHO   - Path to base container: %SIM_ACR_PATH%/fmu_base:latest
@ECHO   - Dockerfile-windows_FMU_RUN_TIME
@ECHO Service steps for service hookup:
@ECHO   - Pushing to MCR (with :version)
@ECHO   - Edit YAML file about it
@ECHO   - Wait for it to be approved in repo
@ECHO   - Tag container and push to bonsai sim prod
@ECHO   - Status link to check what has been published
@ECHO   - Register base image
@ECHO   - Make cosmos record