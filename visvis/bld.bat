%PYTHON% setup.py install
%PYTHON% -c "import visvis.utils.iso" 
if errorlevel 1 exit 1