@REM Download 7zip executable if it doesn't exist
if not exist "7z1900-x64.msi" (
    echo "Downloading 7zip installer executable"
    powershell -Command "Invoke-WebRequest https://www.7-zip.org/a/7z1900-x64.msi -OutFile 7z1900-x64.msi"
) else (
    echo "7zip installer already downloaded"
)

@REM Install 7zip
echo "Installing 7zip for decompressing some .7z files (you should use it as well, better than rar and is free)"
.\7z1900-x64.msi

python.exe -m venv mmv_python_virtual_env
source .\mmv_python_virtual_env\scripts\activate.bat

@REM Upgrade pip
echo "Upgrading Python's package manager PIP and wheel"
python.exe -m pip install --upgrade pip wheel --user

@REM If you have any troubles with lapack / blas with SciPy try removing the @REM on the next line..?
@REM python.exe -m pip install -U https://download.lfd.uci.edu/pythonlibs/z4tqcw5k/scipy-1.5.4-cp38-cp38-win_amd64.whl scipy

echo "Installing MMV Python dependencies"
python.exe -m pip install -r "..\..\mmv\requirements.txt" --user

echo "Installing every dependency we'll need (hopefully)"
python.exe ".\get_externals.py"