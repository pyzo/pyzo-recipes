#!/bin/bash

if [ `uname` == Linux ]; then
    $PYTHON setup.py install
fi


if [ `uname` == Darwin ]; then

    # This does not work:
    #sudo python3.3 setup.py install
    
    # So install cx_freeze in whatever way in native python
    
    # Test
    python3.3 -c 'import cx_Freeze'
    
    # Install from there
    $PYTHON $RECIPE_DIR/../pyside-pyzo/build_from_installed.py /opt/local/Library/Frameworks/Python.framework/Versions/3.3/lib/python3.3/site-packages/cx_Freeze
    
fi
