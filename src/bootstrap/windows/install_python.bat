@REM Download Python executable if it doesn't exist
if not exist "python-3.8.3-amd64.exe" (
    echo "Downloading Python installer executable"
    powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe -OutFile python-3.8.3-amd64.exe"
) else (
    echo Python installer already downloaded
)

@REM Install Python
echo "Installing Python 3.8.3, quiet and unattended, adding Python to PATH, it'll probably ask admin permissions to copy files.."
.\python-3.8.3-amd64.exe /quiet PrependPath=1 CompileAll=1