%PYTHON% setup.py install

REM use this to set release: setenv /x64 /release

REM Prepare for compiling with MS SDK
%PYTHON% %RECIPE_DIR%\patch_for_utils_compile.py

REM These must be commented on win32
set MSSdk=1
set DISTUTILS_USE_SDK=1

REM import twice, because first one tends to fail
%PYTHON% -c "import visvis.utils.iso" 
%PYTHON% -c "import visvis.utils.iso" 

REM we created __pycache__ dirs in numpy during the build
rmdir /s /q %SP_DIR%\numpy

if errorlevel 1 exit 
