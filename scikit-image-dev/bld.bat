REM Exec these before running the build
REM setenv /x64 /release 
REM set DISTUTILS_USE_SDK=1 
REM set MSSdk=1

cd C:\almar\devel\_scikit-image
%PYTHON% setup.py install
if errorlevel 1 exit 1