#!/bin/bash

# Install
$PYTHON setup.py install

# Invoke Cython build
$PYTHON -c 'import visvis.utils.iso' 
