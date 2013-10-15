#!/bin/bash

#export PATH=$PATH:$PREFIX/bin

# Go into dir that contains
# shiboken, pyside and pyside tools
cd sources

# ------------------------- PATCHELF
cd patchelf # So next cd .. works
if [ `uname` != Darwin ]; then
    g++ patchelf.cc -o patchelf
    cp patchelf $PREFIX/bin/patchelf
fi

# ------------------------- SHIBOKEN
cd ..
cd shiboken
mkdir build
cd build


# Patch MakeLists.txt to make it use Python3
$PYTHON -c '
import sys
if sys.version_info[0] >= 3:
    print("Patching CMakeLists.txt ...")
    lines = []
    with open("../CMakeLists.txt", "rt") as file:
        for line in file.readlines():
            if "USE_PYTHON3" in line:
                line = line.replace("FALSE", "TRUE")
                print("Patched a line")
            lines.append(line.rstrip())
    open("../CMakeLists.txt", "wt").write("\n".join(lines))
    print("Done patching CMakeLists.txt ...")
'

# This command is going to fail, but it will create a config
# which we can patch and then retry
set +e
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DLIB_INSTALL_DIR=$PREFIX/lib \
    ..
set -e

# Patch CMakeCache.txt to correct paths
$PYTHON -c '
import sys, os, sysconfig
incl_dir = sysconfig.get_path("include")
lib_dir = sys.prefix + "/lib/libpython3.3m.so"
if not os.path.isfile(lib_dir):
  lib_dir = lib_dir.replace(".so",".dylib")
print("Patching build/CMakeCache.txt ...")
lines = []
with open("CMakeCache.txt", "rt") as file:
    for line in file.readlines():
        if "PYTHON3_INCLUDE_DIR:PATH" in line:
            #line = line.replace("PYTHON3_INCLUDE_DIR-NOTFOUND", incl_dir)
            line = line.split("=")[0] + "=" + incl_dir  # Force!
            print("Patched a line")
        if "PYTHON3_LIBRARY:FILEPATH" in line:
            line = line.replace("PYTHON3_LIBRARY-NOTFOUND", lib_dir)
            print("Patched a line")
        lines.append(line.rstrip())
open("CMakeCache.txt", "wt").write("\n".join(lines))
print("Done patching build/CMakeCache.txt ...")
'

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DLIB_INSTALL_DIR=$PREFIX/lib \
    ..

make VERBOSE=2
make install


# ------------------------- PYSIDE
cd ..
cd ..
cd pyside
mkdir build
cd build

# For some reason, QtCore is not found, 
# so add the lib dir to library search path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PREFIX/lib

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DPYTHON_EXECUTABLE=$PYTHON \
    -DLIB_INSTALL_DIR=$PREFIX/lib \
    -DShiboken_DIR=$PREFIX \
    ..
make
make install



# ------------------------- PYSIDE-TOOLS
cd ..
cd ..
cd pyside-tools
mkdir build
cd build

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DPYTHON_EXECUTABLE=$PYTHON \
    -DLIB_INSTALL_DIR=$PREFIX/lib \
    -DShiboken_DIR=$PREFIX \
    ..
make
make install


# ------ Fixing up dependencies and RPATH and all that

$PYTHON ~/py/pyzo_build/build_from_installed.py shiboken
$PYTHON ~/py/pyzo_build/build_from_installed.py PySide

$PYTHON ~/py/pyzo_build/build_from_installed.py /opt/local/bin/linguist $PREFIX/bin
$PYTHON ~/py/pyzo_build/build_from_installed.py /opt/local/bin/lrelease $PREFIX/bin
$PYTHON ~/py/pyzo_build/build_from_installed.py /opt/local/bin/lupdate $PREFIX/bin

$PYTHON ~/py/pyzo_build/build_from_installed.py $PREFIX/bin/pyside-lupdate $PREFIX/bin
$PYTHON ~/py/pyzo_build/build_from_installed.py $PREFIX/bin/pyside-uic $PREFIX/bin
$PYTHON ~/py/pyzo_build/build_from_installed.py $PREFIX/bin/pyside-rcc $PREFIX/bin
$PYTHON ~/py/pyzo_build/build_from_installed.py $PREFIX/bin/shiboken $PREFIX/bin

# Install qt_menu.nib
$PYTHON $RECIPE_DIR/qt_menu_nib.py
